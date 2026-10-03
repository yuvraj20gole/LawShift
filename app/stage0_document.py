"""Stage 0 — Document ingestion and text extraction.

Extracts text from uploaded typed documents (e.g. PDFs) or scanned/image-based
documents (via Tesseract OCR) and feeds the extracted text directly into Stage 1-4
NLP pipeline.
"""
from __future__ import annotations

import io
from PIL import Image
import pdf2image
import pdfplumber
import pytesseract


def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, bool]:
    """
    Returns (extracted_text, has_extractable_text).
    has_extractable_text=False signals this PDF likely needs OCR
    (scanned/image-based) rather than direct extraction - used later
    to decide whether to fall back to OCR.
    """
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    full_text = "\n\n".join(text_parts)
    # Heuristic: if we got almost no text from a multi-page PDF, it's
    # probably scanned and needs OCR instead
    has_extractable_text = len(full_text.strip()) > 50
    return full_text, has_extractable_text


def extract_text_via_ocr_from_pdf(file_bytes: bytes) -> str:
    """Fallback for scanned PDFs with no extractable text layer."""
    images = pdf2image.convert_from_bytes(file_bytes, dpi=300)
    text_parts: list[str] = []
    for img in images:
        page_text = pytesseract.image_to_string(img, lang="eng")
        if page_text:
            text_parts.append(page_text.strip())
    return "\n\n".join(text_parts)


def extract_text_from_image(file_bytes: bytes) -> str:
    """For direct image uploads (e.g. a phone photo or screenshot of a document)."""
    img = Image.open(io.BytesIO(file_bytes))
    return pytesseract.image_to_string(img, lang="eng").strip()
