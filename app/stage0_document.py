"""Stage 0 — Document text extraction (no pipeline, no storage).

``extract_document`` is the single entry used by ``/api/documents/extract``
and the legacy ``/api/upload_document`` route. Never logs file bytes or text.
"""
from __future__ import annotations

import io
import re
import tempfile
import time
import zipfile
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal

from PIL import Image, ImageFile, ImageOps

from . import stage1

# Cap before PIL raises DecompressionBombError (40 megapixels).
Image.MAX_IMAGE_PIXELS = 40_000_000
ImageFile.LOAD_TRUNCATED_IMAGES = False

MAX_TEXT_CHARS = 20_000
MAX_PDF_PAGES = 30
MAX_OCR_PAGES = 10
PAGE_TYPED_MIN_CHARS = 40
MAX_ZIP_UNCOMPRESSED = 50 * 1024 * 1024
MAX_ZIP_ENTRIES = 2000
OCR_TOTAL_TIMEOUT_SEC = 90.0
DATE_CONTEXT_CHARS = 60
MAX_DATE_CANDIDATES = 5

Kind = Literal["pdf", "image", "docx"]
ReadMethod = Literal["typed", "ocr", "docx"]


class ExtractError(Exception):
    """Structured extraction failure (mapped to HTTP by the route)."""

    def __init__(self, code: str, message: str, status: int = 422):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status


@dataclass
class DateCandidate:
    iso: str
    label: str
    context: str


@dataclass
class ExtractResult:
    filename: str
    kind: Kind
    read_method: ReadMethod
    pages: int | None
    char_count: int
    text: str
    truncated: bool
    date: dict[str, str] | None
    date_candidates: list[dict[str, str]]
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "kind": self.kind,
            "read_method": self.read_method,
            "pages": self.pages,
            "char_count": self.char_count,
            "text": self.text,
            "truncated": self.truncated,
            "date": self.date,
            "date_candidates": self.date_candidates,
            "warnings": list(self.warnings),
        }


def sniff_document_kind(data: bytes) -> Kind | None:
    """Return pdf | image | docx from bytes only (ignore name/MIME)."""
    if data[:4] == b"%PDF":
        return "pdf"
    if len(data) >= 3 and data[:3] == b"\xff\xd8\xff":
        return "image"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image"
    if data[:2] == b"PK":
        if _zip_looks_like_docx(data):
            return "docx"
    return None


def _zip_looks_like_docx(data: bytes) -> bool:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            names = set(zf.namelist())
            return (
                "[Content_Types].xml" in names
                and "word/document.xml" in names
            )
    except zipfile.BadZipFile:
        return False


def _check_zip_bomb(zf: zipfile.ZipFile) -> None:
    infos = zf.infolist()
    if len(infos) > MAX_ZIP_ENTRIES:
        raise ExtractError(
            "zip_too_many_entries",
            "Archive has too many entries.",
            status=422,
        )
    total = 0
    for info in infos:
        total += int(info.file_size)
        if total > MAX_ZIP_UNCOMPRESSED:
            raise ExtractError(
                "zip_too_large",
                "Archive expands beyond the size limit.",
                status=422,
            )


def _docx_has_macros(zf: zipfile.ZipFile) -> bool:
    for name in zf.namelist():
        lower = name.lower()
        if "vbaproject" in lower or lower.endswith(".bin") and "macro" in lower:
            return True
        if lower.startswith("word/vba"):
            return True
    return False


def normalize_text(text: str) -> str:
    # Strip C0/C1 controls except tab/newline; normalise whitespace.
    cleaned = "".join(
        ch if ch in "\t\n\r" or (ord(ch) >= 32 and ord(ch) != 127) else " "
        for ch in (text or "")
    )
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def truncate_text(text: str) -> tuple[str, bool]:
    if len(text) <= MAX_TEXT_CHARS:
        return text, False
    return text[:MAX_TEXT_CHARS], True


def _format_label(d: date) -> str:
    try:
        return d.strftime("%-d %B %Y")
    except ValueError:
        return d.strftime("%d %B %Y").lstrip("0")


def _context_around(text: str, span: str, width: int = DATE_CONTEXT_CHARS) -> str:
    if not span:
        return text[: width * 2]
    idx = text.lower().find(span.lower())
    if idx < 0:
        return (text[: width * 2]).strip()
    start = max(0, idx - width)
    end = min(len(text), idx + len(span) + width)
    snippet = text[start:end].strip()
    if start > 0:
        snippet = "…" + snippet
    if end < len(text):
        snippet = snippet + "…"
    return snippet


def collect_date_candidates(text: str) -> tuple[dict[str, str] | None, list[dict[str, str]], list[str]]:
    """Run Stage 1 on whole text and each line; up to 5 distinct dates."""
    warnings: list[str] = []
    chosen_date, chosen_span, _ = stage1.extract_offense_date(text)
    primary: dict[str, str] | None = None
    if chosen_date is not None:
        primary = {
            "iso": chosen_date.isoformat(),
            "label": _format_label(chosen_date),
        }

    by_iso: dict[str, DateCandidate] = {}
    # Whole-text hit first so it stays preferred in ordering.
    if chosen_date is not None:
        iso = chosen_date.isoformat()
        by_iso[iso] = DateCandidate(
            iso=iso,
            label=_format_label(chosen_date),
            context=_context_around(text, chosen_span or ""),
        )

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        d, span, _ = stage1.extract_offense_date(line)
        if d is None:
            continue
        iso = d.isoformat()
        if iso in by_iso:
            continue
        by_iso[iso] = DateCandidate(
            iso=iso,
            label=_format_label(d),
            context=_context_around(line, span or "", width=DATE_CONTEXT_CHARS),
        )
        if len(by_iso) >= MAX_DATE_CANDIDATES:
            break

    candidates = [
        {"iso": c.iso, "label": c.label, "context": c.context}
        for c in by_iso.values()
    ][:MAX_DATE_CANDIDATES]
    if len(candidates) > 1:
        warnings.append("multiple_dates")
    return primary, candidates, warnings


# ---------------------------------------------------------------------------
# Legacy helpers (kept for callers / tests that import them directly)
# ---------------------------------------------------------------------------


def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, bool]:
    """Legacy: (text, has_extractable_text). Prefer ``extract_document``."""
    import pdfplumber

    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages[:MAX_PDF_PAGES]:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    full_text = "\n\n".join(text_parts)
    has_extractable_text = len(full_text.strip()) > 50
    return full_text, has_extractable_text


def extract_text_via_ocr_from_pdf(file_bytes: bytes) -> str:
    """Legacy OCR fallback for scanned PDFs."""
    import pdf2image
    import pytesseract

    images = pdf2image.convert_from_bytes(file_bytes, dpi=300)[:MAX_OCR_PAGES]
    text_parts: list[str] = []
    for img in images:
        page_text = pytesseract.image_to_string(img, lang="eng")
        if page_text:
            text_parts.append(page_text.strip())
    return "\n\n".join(text_parts)


def extract_text_from_image(file_bytes: bytes) -> str:
    """Legacy image OCR."""
    import pytesseract

    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.load()
        # Phone JPEGs often store a sideways buffer + EXIF Orientation.
        # Apply it so OCR sees upright pixels; no-op when EXIF is absent.
        img = ImageOps.exif_transpose(img) or img
    except Image.DecompressionBombError as exc:
        raise ExtractError(
            "image_too_large",
            "Image exceeds the pixel limit.",
            status=422,
        ) from exc
    return pytesseract.image_to_string(img, lang="eng").strip()


# ---------------------------------------------------------------------------
# Unified extractor
# ---------------------------------------------------------------------------


def _extract_docx(data: bytes) -> tuple[str, int | None, list[str]]:
    from docx import Document

    warnings: list[str] = []
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            _check_zip_bomb(zf)
            if _docx_has_macros(zf):
                raise ExtractError(
                    "macros_not_allowed",
                    "Macro-enabled Word files are not accepted.",
                    status=422,
                )
        doc = Document(str(tmp_path))
        parts: list[str] = []
        # Document order: body paragraphs and tables as they appear is
        # approximated by iterating paragraphs then tables (python-docx
        # limitation). Prefer XML body order when available.
        try:
            from docx.oxml.ns import qn

            body = doc.element.body
            for child in body.iterchildren():
                tag = child.tag
                if tag == qn("w:p"):
                    from docx.text.paragraph import Paragraph

                    p = Paragraph(child, doc)
                    t = (p.text or "").strip()
                    if t:
                        parts.append(t)
                elif tag == qn("w:tbl"):
                    from docx.table import Table

                    table = Table(child, doc)
                    for row in table.rows:
                        cells = [
                            (c.text or "").strip()
                            for c in row.cells
                            if (c.text or "").strip()
                        ]
                        if cells:
                            parts.append("\t".join(cells))
        except Exception:
            parts = []
            for p in doc.paragraphs:
                t = (p.text or "").strip()
                if t:
                    parts.append(t)
            for table in doc.tables:
                for row in table.rows:
                    cells = [
                        (c.text or "").strip()
                        for c in row.cells
                        if (c.text or "").strip()
                    ]
                    if cells:
                        parts.append("\t".join(cells))
        return "\n".join(parts), None, warnings
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass


def _extract_pdf(data: bytes) -> tuple[str, ReadMethod, int, list[str]]:
    import pdfplumber

    warnings: list[str] = []
    try:
        pdf = pdfplumber.open(io.BytesIO(data))
    except Exception as exc:  # noqa: BLE001
        msg = str(exc).lower()
        if "password" in msg or "encrypted" in msg:
            raise ExtractError(
                "password_protected",
                "This PDF is password-protected.",
                status=422,
            ) from exc
        raise ExtractError(
            "unreadable",
            "Could not read this PDF.",
            status=422,
        ) from exc

    try:
        if getattr(pdf, "is_encrypted", False):
            # pdfplumber may open encrypted files with empty password.
            try:
                n = len(pdf.pages)
            except Exception as exc:  # noqa: BLE001
                raise ExtractError(
                    "password_protected",
                    "This PDF is password-protected.",
                    status=422,
                ) from exc
            if n == 0:
                raise ExtractError(
                    "password_protected",
                    "This PDF is password-protected.",
                    status=422,
                )

        total_pages = len(pdf.pages)
        pages_to_read = min(total_pages, MAX_PDF_PAGES)
        if total_pages > MAX_PDF_PAGES:
            warnings.append("pages_skipped")

        typed_parts: list[str] = []
        weak_pages: list[int] = []
        for i in range(pages_to_read):
            page = pdf.pages[i]
            try:
                page_text = page.extract_text() or ""
            except Exception:
                page_text = ""
            if len(page_text.strip()) < PAGE_TYPED_MIN_CHARS:
                weak_pages.append(i)
            typed_parts.append(page_text)

        typed_joined = "\n\n".join(typed_parts)
        need_ocr = bool(weak_pages) or len(typed_joined.strip()) < PAGE_TYPED_MIN_CHARS

        if not need_ocr:
            return typed_joined, "typed", pages_to_read, warnings

        # OCR fallback for weak / empty pages (cap OCR page count).
        ocr_indices = weak_pages[:MAX_OCR_PAGES]
        if len(weak_pages) > MAX_OCR_PAGES or total_pages > MAX_PDF_PAGES:
            if "pages_skipped" not in warnings:
                warnings.append("pages_skipped")

        ocr_text_by_page: dict[int, str] = {}
        if ocr_indices:
            ocr_text_by_page = _ocr_pdf_pages(data, ocr_indices, warnings)

        merged: list[str] = []
        used_ocr = False
        for i in range(pages_to_read):
            if i in ocr_text_by_page and ocr_text_by_page[i].strip():
                merged.append(ocr_text_by_page[i])
                used_ocr = True
            else:
                merged.append(typed_parts[i])

        method: ReadMethod = "ocr" if used_ocr else "typed"
        if used_ocr:
            warnings.append("ocr_may_misread_digits")
        return "\n\n".join(merged), method, pages_to_read, warnings
    finally:
        pdf.close()


def _ocr_pdf_pages(
    data: bytes, page_indices: list[int], warnings: list[str]
) -> dict[int, str]:
    import pdf2image
    import pytesseract

    if not page_indices:
        return {}
    # pdf2image uses 1-based first/last page.
    first = min(page_indices) + 1
    last = max(page_indices) + 1
    deadline = time.monotonic() + OCR_TOTAL_TIMEOUT_SEC
    try:
        images = pdf2image.convert_from_bytes(
            data, dpi=200, first_page=first, last_page=last
        )
    except Exception:
        return {}

    out: dict[int, str] = {}
    for offset, img in enumerate(images):
        page_i = first - 1 + offset
        if page_i not in page_indices:
            continue
        if time.monotonic() > deadline:
            warnings.append("pages_skipped")
            break
        try:
            out[page_i] = pytesseract.image_to_string(img, lang="eng").strip()
        except Exception:
            out[page_i] = ""
    return out


def _extract_image(data: bytes) -> tuple[str, list[str]]:
    import pytesseract

    warnings: list[str] = ["ocr_may_misread_digits"]
    try:
        img = Image.open(io.BytesIO(data))
        # Trigger pixel-count check (respects Image.MAX_IMAGE_PIXELS).
        img.load()
        # Phone JPEGs often store a sideways buffer + EXIF Orientation
        # (e.g. tag 6). Transpose before OCR so text is upright. Safe when
        # there is no EXIF: exif_transpose returns a copy or the same image.
        img = ImageOps.exif_transpose(img) or img
    except Image.DecompressionBombError as exc:
        raise ExtractError(
            "image_too_large",
            "Image exceeds the 40 megapixel limit.",
            status=422,
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise ExtractError(
            "unreadable",
            "Could not read this image.",
            status=422,
        ) from exc

    deadline = time.monotonic() + OCR_TOTAL_TIMEOUT_SEC
    try:
        text = pytesseract.image_to_string(img, lang="eng")
    except Exception as exc:  # noqa: BLE001
        raise ExtractError(
            "unreadable",
            "OCR failed for this image.",
            status=422,
        ) from exc
    if time.monotonic() > deadline:
        warnings.append("pages_skipped")
    return text or "", warnings


def extract_document(data: bytes, filename: str) -> ExtractResult:
    """Extract text and date candidates. Raises ``ExtractError`` on failure."""
    if not data:
        raise ExtractError("empty", "Empty file.", status=422)

    kind = sniff_document_kind(data)
    if kind is None:
        raise ExtractError(
            "unsupported_type",
            "Unsupported file type. PDF, JPEG, PNG, and DOCX are supported.",
            status=415,
        )

    safe_name = (filename or "document").replace("\x00", "")[:200]
    warnings: list[str] = []
    pages: int | None = None
    read_method: ReadMethod

    if kind == "docx":
        text, pages, w = _extract_docx(data)
        warnings.extend(w)
        read_method = "docx"
    elif kind == "pdf":
        text, read_method, pages, w = _extract_pdf(data)
        warnings.extend(w)
    else:
        text, w = _extract_image(data)
        warnings.extend(w)
        read_method = "ocr"
        pages = 1

    text = normalize_text(text)
    text, truncated = truncate_text(text)
    if truncated:
        warnings.append("truncated")

    if not text:
        warnings.append("no_text_found")
        raise ExtractError(
            "no_text_found",
            "Could not extract readable text from this document.",
            status=422,
        )

    primary, candidates, date_warnings = collect_date_candidates(text)
    for w in date_warnings:
        if w not in warnings:
            warnings.append(w)

    # Deduplicate warnings, stable order.
    seen: set[str] = set()
    ordered: list[str] = []
    for w in warnings:
        if w not in seen:
            seen.add(w)
            ordered.append(w)

    return ExtractResult(
        filename=safe_name,
        kind="image" if kind == "image" else kind,
        read_method=read_method,
        pages=pages,
        char_count=len(text),
        text=text,
        truncated=truncated,
        date=primary,
        date_candidates=candidates,
        warnings=ordered,
    )
