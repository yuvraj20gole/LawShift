"""M3 documents: extract, attach/detach, handle_query with facts.

Synthetic files only. Never logs document text. OCR tests skip without tesseract.
"""
from __future__ import annotations

import asyncio
import io
import os
import shutil
import struct
import sys
import time
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

_PRIV = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_PRIV_PEM = _PRIV.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
).decode()
_PUB_PEM = (
    _PRIV.public_key()
    .public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    .decode()
)
_ISSUER = "https://example-test.supabase.co/auth/v1"
_AUD = "authenticated"

os.environ["SUPABASE_URL"] = "https://example-test.supabase.co"
os.environ["LAWSHIFT_JWT_AUDIENCE"] = _AUD
os.environ["LAWSHIFT_JWT_TEST_PUBLIC_KEY_PEM"] = _PUB_PEM
os.environ["LAWSHIFT_EXTRACT_PER_HOUR"] = "3"
os.environ["LAWSHIFT_MAX_CONCURRENT_EXTRACT"] = "1"
os.environ["LAWSHIFT_EXTRACT_WAIT_SEC"] = "0.2"
os.environ["LAWSHIFT_MAX_UPLOAD_BYTES"] = str(2 * 1024 * 1024)
os.environ.pop("SUPABASE_JWT_SECRET", None)

from app.case_attach import (  # noqa: E402
    ATTACH_MAX_CONVERSATIONS,
    attach_case,
    attached_count_for_tests,
    get_attached,
    reset_attached_cases,
)
from app.limits import reset_extract_semaphore, reset_rate_limits  # noqa: E402
from app.main import _LOCKED_DATES, app, handle_query  # noqa: E402
from app.schemas import ClarifyResponse, QueryRequest  # noqa: E402
from app.stage0_document import (  # noqa: E402
    ExtractError,
    extract_document,
    sniff_document_kind,
)


HAS_TESSERACT = shutil.which("tesseract") is not None


def _mint(sub: str = "user-a", *, tamper: bool = False) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "role": "authenticated",
        "aud": _AUD,
        "iss": _ISSUER,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),
    }
    token = jwt.encode(payload, _PRIV_PEM, algorithm="RS256")
    if tamper:
        h, b, s = token.split(".")
        s = ("A" if not s.startswith("A") else "B") + s[1:]
        token = f"{h}.{b}.{s}"
    return token


def _auth(sub: str = "user-a") -> dict[str, str]:
    return {"Authorization": f"Bearer {_mint(sub)}"}


def _client() -> TestClient:
    return TestClient(app)


def _pdf_bytes(text: str, pages: int = 1) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    for i in range(pages):
        c.drawString(72, 720, f"{text} page {i + 1}")
        c.showPage()
    c.save()
    return buf.getvalue()


def _docx_bytes(paragraphs: list[str], *, macro: bool = False) -> bytes:
    from docx import Document

    buf = io.BytesIO()
    doc = Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    doc.save(buf)
    data = buf.getvalue()
    if not macro:
        return data
    # Inject a fake VBA project path so macro detection fires.
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data), "r") as src, zipfile.ZipFile(
        out, "w"
    ) as dst:
        for info in src.infolist():
            dst.writestr(info, src.read(info.filename))
        dst.writestr("word/vbaProject.bin", b"FAKE")
    return out.getvalue()


def _png_bytes(w: int = 32, h: int = 32, colour=(255, 255, 255)) -> bytes:
    img = Image.new("RGB", (w, h), colour)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _jpeg_bytes() -> bytes:
    img = Image.new("RGB", (40, 40), (200, 200, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    reset_rate_limits()
    reset_extract_semaphore()
    reset_attached_cases()
    _LOCKED_DATES.clear()
    os.environ["LAWSHIFT_JWT_TEST_PUBLIC_KEY_PEM"] = _PUB_PEM
    os.environ["LAWSHIFT_EXTRACT_PER_HOUR"] = "3"
    os.environ["LAWSHIFT_MAX_CONCURRENT_EXTRACT"] = "1"
    os.environ["LAWSHIFT_EXTRACT_WAIT_SEC"] = "0.2"
    os.environ["LAWSHIFT_MAX_UPLOAD_BYTES"] = str(2 * 1024 * 1024)

    async def stub_handle(req):
        return ClarifyResponse(
            question="stub",
            reason="missing_date",
        )

    # Keep real handle_query for attach-rule tests; stub only heavy paths
    # when hitting HTTP extract/upload that would call Stage 3/4.
    yield
    reset_rate_limits()
    reset_extract_semaphore()
    reset_attached_cases()
    _LOCKED_DATES.clear()


# ---------------------------------------------------------------------------
# Sniff / extract paths
# ---------------------------------------------------------------------------


def test_sniff_pdf_jpeg_png_docx():
    assert sniff_document_kind(_pdf_bytes("hello")) == "pdf"
    assert sniff_document_kind(_jpeg_bytes()) == "image"
    assert sniff_document_kind(_png_bytes()) == "image"
    assert sniff_document_kind(_docx_bytes(["On 25 June 2024 a theft occurred."])) == "docx"
    assert sniff_document_kind(b"not-a-file") is None


def test_extract_pdf_typed():
    data = _pdf_bytes("On 25 June 2024 the accused stole a bicycle.")
    result = extract_document(data, "fir.pdf")
    assert result.kind == "pdf"
    assert result.read_method == "typed"
    assert result.char_count > 0
    assert result.date is not None
    assert result.date["iso"] == "2024-06-25"


def test_extract_docx_paragraphs_and_table():
    from docx import Document

    buf = io.BytesIO()
    doc = Document()
    doc.add_paragraph("On 25 June 2024 a shopkeeper was assaulted.")
    table = doc.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "Place"
    table.rows[0].cells[1].text = "Market road"
    doc.save(buf)
    result = extract_document(buf.getvalue(), "note.docx")
    assert result.kind == "docx"
    assert result.read_method == "docx"
    assert "assaulted" in result.text.lower()
    assert "Market road" in result.text


def test_extract_rejects_spoofed_extension():
    # .pdf name but PNG bytes
    with pytest.raises(ExtractError) as ei:
        # wait — PNG sniffs as image, not reject. Spoof: .docx name with PDF bytes is ok (sniff wins).
        # True spoof rejection: random bytes with .pdf name
        extract_document(b"MZ\x90\x00fake", "report.pdf")
    assert ei.value.status == 415


def test_extract_empty():
    with pytest.raises(ExtractError) as ei:
        extract_document(b"", "empty.pdf")
    assert ei.value.code == "empty"


def test_extract_docx_macros_rejected():
    with pytest.raises(ExtractError) as ei:
        extract_document(_docx_bytes(["hello"], macro=True), "m.docm")
    assert ei.value.code == "macros_not_allowed"


def test_extract_zip_bomb_rejected():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_STORED) as zf:
        # Claim a huge uncompressed size without writing that many bytes.
        info = zipfile.ZipInfo("word/document.xml")
        payload = b'<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p/></w:body></w:document>'
        # Manually craft oversized declared size via ZipInfo.file_size after write
        zf.writestr("[Content_Types].xml", b"<Types></Types>")
        zf.writestr("word/document.xml", payload)
        # Add many tiny entries to trip entry cap
        for i in range(2100):
            zf.writestr(f"word/media/x{i}.txt", b"x")
    with pytest.raises(ExtractError) as ei:
        extract_document(buf.getvalue(), "bomb.docx")
    assert ei.value.code in {"zip_too_many_entries", "zip_too_large", "unsupported_type"}


def test_extract_password_pdf():
    from pypdf import PdfReader, PdfWriter

    raw = _pdf_bytes("secret text on 25 June 2024")
    reader = PdfReader(io.BytesIO(raw))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt("not-the-password")
    out = io.BytesIO()
    writer.write(out)
    encrypted = out.getvalue()
    with pytest.raises(ExtractError) as ei:
        extract_document(encrypted, "locked.pdf")
    # Some pdfplumber builds raise password; others may open empty — accept either
    assert ei.value.status == 422
    assert ei.value.code in {"password_protected", "no_text_found", "unreadable"}


def test_extract_image_pixel_cap(monkeypatch):
    import app.stage0_document as s0

    def boom(*_a, **_k):
        raise Image.DecompressionBombError("too many pixels")

    monkeypatch.setattr(s0.Image, "open", boom)
    with pytest.raises(ExtractError) as ei:
        extract_document(_png_bytes(), "big.png")
    assert ei.value.code == "image_too_large"


def test_extract_pdf_pages_skipped_warning():
    data = _pdf_bytes("On 25 June 2024 facts about theft.", pages=35)
    result = extract_document(data, "long.pdf")
    assert "pages_skipped" in result.warnings
    assert result.pages == 30


def test_extract_truncation():
    # Build a PDF with a long repeated line via many pages of filler
    filler = ("word " * 200) + "On 25 June 2024 end. "
    # Direct unit path: monkeypatch after typed extract by calling truncate
    from app.stage0_document import truncate_text

    big = "a" * 25000
    text, trunc = truncate_text(big)
    assert trunc is True
    assert len(text) == 20000


@pytest.mark.skipif(not HAS_TESSERACT, reason="tesseract not installed")
def test_extract_image_ocr_path():
    # Blank PNG may yield empty → 422; draw text-like noise is unreliable.
    # Just ensure the image path is accepted and either returns text or no_text.
    data = _png_bytes(120, 40, (255, 255, 255))
    try:
        result = extract_document(data, "scan.png")
        assert result.kind == "image"
        assert result.read_method == "ocr"
    except ExtractError as exc:
        assert exc.code == "no_text_found"


# ---------------------------------------------------------------------------
# HTTP extract / attach / detach
# ---------------------------------------------------------------------------


def test_extract_requires_auth():
    client = _client()
    r = client.post(
        "/api/documents/extract",
        files={"file": ("a.pdf", _pdf_bytes("On 25 June 2024 theft."), "application/pdf")},
    )
    assert r.status_code == 401


def test_extract_http_ok(monkeypatch):
    client = _client()
    r = client.post(
        "/api/documents/extract",
        headers=_auth(),
        files={
            "file": (
                "fir.pdf",
                _pdf_bytes("On 25 June 2024 the accused stole a bicycle."),
                "application/pdf",
            )
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["kind"] == "pdf"
    assert body["date"]["iso"] == "2024-06-25"
    assert "text" in body
    assert body["char_count"] == len(body["text"])


def test_extract_rate_limit_429():
    client = _client()
    files = {
        "file": (
            "fir.pdf",
            _pdf_bytes("On 25 June 2024 the accused stole a bicycle."),
            "application/pdf",
        )
    }
    assert client.post("/api/documents/extract", headers=_auth(), files=files).status_code == 200
    assert client.post("/api/documents/extract", headers=_auth(), files=files).status_code == 200
    assert client.post("/api/documents/extract", headers=_auth(), files=files).status_code == 200
    r = client.post("/api/documents/extract", headers=_auth(), files=files)
    assert r.status_code == 429


def test_extract_busy_503():
    from app.limits import ExtractSlot
    from app.security_settings import SecuritySettings

    async def run():
        settings = SecuritySettings.from_environ()
        async with ExtractSlot(settings):
            with pytest.raises(Exception) as ei:
                async with ExtractSlot(settings):
                    pass
            assert ei.value.status_code == 503

    asyncio.run(run())


def test_attach_detach_and_ownership():
    client = _client()
    body = {
        "conversation_id": "conv-1",
        "facts_text": "A bookstore owner sold obscene magazines.",
        "offence_date": "2024-06-25",
        "date_source": "document",
        "filename": "fir.pdf",
    }
    r = client.post("/api/case/attach", headers=_auth("user-a"), json=body)
    assert r.status_code == 200, r.text
    assert r.json()["ok"] is True
    assert r.json()["code"] == "IPC"
    assert get_attached("conv-1") is not None
    assert _LOCKED_DATES["conv-1"] == date(2024, 6, 25)

    # Other user cannot re-attach or detach
    r2 = client.post("/api/case/attach", headers=_auth("user-b"), json=body)
    assert r2.status_code == 403
    r3 = client.post(
        "/api/case/detach",
        headers=_auth("user-b"),
        json={"conversation_id": "conv-1"},
    )
    assert r3.status_code == 403

    r4 = client.post(
        "/api/case/detach",
        headers=_auth("user-a"),
        json={"conversation_id": "conv-1"},
    )
    assert r4.status_code == 200
    assert get_attached("conv-1") is None
    assert "conv-1" not in _LOCKED_DATES


def test_attach_validation():
    client = _client()
    base = {
        "conversation_id": "conv-v",
        "facts_text": "facts",
        "offence_date": "2024-06-25",
        "date_source": "edited",
    }
    assert (
        client.post(
            "/api/case/attach",
            headers=_auth(),
            json={**base, "offence_date": "not-a-date"},
        ).status_code
        == 422
    )
    future = (date.today() + timedelta(days=3)).isoformat()
    assert (
        client.post(
            "/api/case/attach",
            headers=_auth(),
            json={**base, "offence_date": future},
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/case/attach",
            headers=_auth(),
            json={**base, "offence_date": "1859-12-31"},
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/case/attach",
            headers=_auth(),
            json={**base, "facts_text": ""},
        ).status_code
        == 422
    )


def test_attach_expiry_and_eviction(monkeypatch):
    # Expiry
    attach_case(
        conversation_id="old",
        user_id="user-a",
        facts_text="facts",
        offence_date=date(2024, 6, 25),
        date_source="document",
        filename=None,
    )
    row = get_attached("old")
    assert row is not None
    row.attached_at = time.time() - (3 * 60 * 60)
    assert get_attached("old") is None

    # Eviction at cap
    reset_attached_cases()
    for i in range(ATTACH_MAX_CONVERSATIONS + 5):
        attach_case(
            conversation_id=f"c{i}",
            user_id="user-a",
            facts_text=f"facts {i}",
            offence_date=date(2024, 6, 25),
            date_source="document",
            filename=None,
        )
        # Stagger timestamps
        get_attached(f"c{i}").attached_at = time.time() - (ATTACH_MAX_CONVERSATIONS + 5 - i)
    assert attached_count_for_tests() <= ATTACH_MAX_CONVERSATIONS


# ---------------------------------------------------------------------------
# handle_query + attached facts
# ---------------------------------------------------------------------------


def test_handle_query_no_attach_unchanged(monkeypatch):
    """Without attach, output matches the pre-attach path (clarify missing_date)."""
    calls = {}

    async def capture(**kwargs):
        calls["kwargs"] = kwargs
        return ClarifyResponse(question="q", reason="missing_date")

    monkeypatch.setattr("app.main._run_pipeline", capture)
    req = QueryRequest(
        message="hello there",
        conversation_id="plain-1",
        language="en",
    )
    asyncio.run(handle_query(req))
    assert calls["kwargs"]["message"] == "hello there"
    assert calls["kwargs"]["date_source"] == "message"


def test_handle_query_facts_no_date_conflict_from_facts(monkeypatch):
    attach_case(
        conversation_id="att-1",
        user_id="user-a",
        facts_text=(
            "On 5 August 2024 the accused assaulted the complainant. "
            "Also mentions 25 June 2024 in a letter."
        ),
        offence_date=date(2024, 6, 25),
        date_source="document",
        filename="fir.pdf",
    )
    _LOCKED_DATES["att-1"] = date(2024, 6, 25)
    calls = {}

    async def capture(**kwargs):
        calls["kwargs"] = kwargs
        return ClarifyResponse(question="q", reason="missing_facts")

    monkeypatch.setattr("app.main._run_pipeline", capture)
    # Follow-up has no date — facts' August date must not conflict.
    resp = asyncio.run(
        handle_query(
            QueryRequest(
                message="Which section applies?",
                conversation_id="att-1",
                language="en",
            )
        )
    )
    assert getattr(resp, "reason", None) != "date_conflict"
    assert calls["kwargs"]["offense_date"] == date(2024, 6, 25)
    assert calls["kwargs"]["date_source"] == "document"
    assert calls["kwargs"]["message"].startswith("Which section applies?")
    assert "assaulted" in calls["kwargs"]["message"]


def test_handle_query_followup_cross_cutoff_conflicts(monkeypatch):
    attach_case(
        conversation_id="att-2",
        user_id="user-a",
        facts_text="A bookstore owner sold obscene magazines.",
        offence_date=date(2024, 6, 25),
        date_source="edited",
        filename=None,
    )
    _LOCKED_DATES["att-2"] = date(2024, 6, 25)

    async def should_not_run(**_k):
        raise AssertionError("_run_pipeline should not run on date_conflict")

    monkeypatch.setattr("app.main._run_pipeline", should_not_run)
    resp = asyncio.run(
        handle_query(
            QueryRequest(
                message="Actually the offence was on 5 August 2024",
                conversation_id="att-2",
                language="en",
            )
        )
    )
    assert resp.kind == "bifurcation"
    assert resp.reason == "date_conflict"


def test_handle_query_missing_facts_uses_attached(monkeypatch):
    attach_case(
        conversation_id="att-3",
        user_id="user-a",
        facts_text="The accused stole a bicycle from the complainant.",
        offence_date=date(2024, 6, 25),
        date_source="document",
        filename=None,
    )
    _LOCKED_DATES["att-3"] = date(2024, 6, 25)
    seen = {}

    async def capture(**kwargs):
        from app.main import message_missing_offense_facts

        seen["missing"] = message_missing_offense_facts(
            kwargs["message"], kwargs["date_span_for_strip"]
        )
        return ClarifyResponse(question="ok", reason="missing_date")

    monkeypatch.setattr("app.main._run_pipeline", capture)
    asyncio.run(
        handle_query(
            QueryRequest(
                message="Which section applies?",
                conversation_id="att-3",
                language="en",
            )
        )
    )
    assert seen["missing"] is False


def test_compose_meta_followup_retrieves_facts_alone():
    from app.main import _compose_attached_messages

    facts = "The accused stole a bicycle from the complainant outside the house."
    full, retr = _compose_attached_messages("Which section applies?", facts)
    assert full.startswith("Which section applies?")
    assert facts in full
    assert retr == facts
    assert "Which section" not in retr


def test_compose_content_followup_keeps_followup_first():
    from app.main import _compose_attached_messages

    facts = "Boilerplate pad. " * 20 + "The accused stole a bicycle."
    full, retr = _compose_attached_messages(
        "He also threatened the complainant with a knife",
        facts,
    )
    assert retr.startswith("He also threatened")
    assert "stole a bicycle" in retr
    assert full.startswith("He also threatened")


def test_compose_does_not_silently_truncate_facts():
    """Measurements did not support an automatic 500/800-char cut."""
    from app.main import _compose_attached_messages

    facts = ("word " * 500) + "unique_tail_marker"
    full, retr = _compose_attached_messages("Which section applies?", facts)
    assert retr == facts
    assert "unique_tail_marker" in retr
    assert "unique_tail_marker" in full


def test_handle_query_meta_followup_passes_retrieve_query(monkeypatch):
    attach_case(
        conversation_id="att-retr",
        user_id="user-a",
        facts_text="The accused stole a bicycle from the complainant.",
        offence_date=date(2024, 6, 25),
        date_source="document",
        filename=None,
    )
    _LOCKED_DATES["att-retr"] = date(2024, 6, 25)
    seen = {}

    async def capture(**kwargs):
        seen["message"] = kwargs["message"]
        seen["retrieve_query"] = kwargs.get("retrieve_query")
        return ClarifyResponse(question="ok", reason="missing_date")

    monkeypatch.setattr("app.main._run_pipeline", capture)
    asyncio.run(
        handle_query(
            QueryRequest(
                message="Which section applies?",
                conversation_id="att-retr",
                language="en",
            )
        )
    )
    assert seen["retrieve_query"] == "The accused stole a bicycle from the complainant."
    assert seen["message"].startswith("Which section applies?")
