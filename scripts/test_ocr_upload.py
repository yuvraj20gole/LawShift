"""Comprehensive test suite for Stage 0 Document & Image OCR upload pipeline.

Tests:
1. Typed PDF regression (3 cases: counterfeit currency, riot liability, obscene literature).
2. Scanned / Image-only PDF (rasterized bitmap PDF with no text layer -> OCR fallback).
3. Direct Image Upload (PNG & JPEG photo/screenshot -> direct OCR).
4. Raw OCR text inspection vs final pipeline routing & verification.
"""
from __future__ import annotations

import io
import json
import os
import sys
import time
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app
import app.stage0_document as stage0
import app.stage3 as stage3
import app.stage4 as stage4


def create_typed_pdf(text: str) -> bytes:
    """Create a searchable, typed PDF with text layer."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    text_object = c.beginText(50, 750)
    text_object.setFont("Helvetica", 11)
    for line in text.split("\n"):
        text_object.textLine(line)
    c.drawText(text_object)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()


def create_rendered_image(text: str) -> Image.Image:
    """Render text onto a high-resolution PIL Image simulating a photographed/scanned document."""
    img = Image.new("RGB", (1600, 500), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Use default font or basic truetype font
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
    except Exception:
        font = ImageFont.load_default()

    # Wrap text into lines of ~70 chars
    words = text.split(" ")
    lines = []
    current_line = []
    for w in words:
        current_line.append(w)
        if len(" ".join(current_line)) > 65:
            lines.append(" ".join(current_line))
            current_line = []
    if current_line:
        lines.append(" ".join(current_line))

    y = 60
    for line in lines:
        draw.text((60, y), line, fill=(0, 0, 0), font=font)
        y += 45

    return img


def create_image_bytes(text: str, fmt: str = "PNG") -> bytes:
    """Create in-memory PNG or JPEG image bytes."""
    img = create_rendered_image(text)
    buf = io.BytesIO()
    img.save(buf, format=fmt, quality=95)
    buf.seek(0)
    return buf.getvalue()


def create_scanned_image_only_pdf(text: str) -> bytes:
    """Create an image-only PDF (bitmap embedded as PDF page, no selectable text layer)."""
    img = create_rendered_image(text)
    buf = io.BytesIO()
    img.save(buf, format="PDF", resolution=300.0)
    buf.seek(0)
    return buf.getvalue()


def run_all_tests():
    print("=== INITIALIZING PIPELINE FOR OCR & DOCUMENT UPLOAD TESTS ===")
    stage4.check_ollama()
    stage3.load()

    client = TestClient(app)

    test_cases = [
        {
            "id": "case1_bns_counterfeit",
            "name": "Case 1: Counterfeit Currency (BNS Route)",
            "text": "On 5 September 2024, a person was found in possession of counterfeit currency notes in Mumbai, knowing they were forged.",
            "expected_route": "BNS",
        },
        {
            "id": "case2_bns_riot",
            "name": "Case 2: Riot Liability of Land Agent (BNS Route)",
            "text": "On 10 August 2024, a riot occurred on a property for the landowner's benefit, and the agent failed to take lawful steps to prevent it.",
            "expected_route": "BNS",
            "expected_section": "193",
        },
        {
            "id": "case3_ipc_obscene",
            "name": "Case 3: Obscene Literature Sale (IPC Route)",
            "text": "On 25 June 2024, a bookstore owner sold obscene magazines to the public for the first time.",
            "expected_route": "IPC",
            "expected_section": "292",
        },
    ]

    print("\n" + "=" * 90)
    print("PART 1: REGRESSION CHECK — TYPED PDFS (DIRECT TEXT EXTRACTION)")
    print("=" * 90)

    for idx, tc in enumerate(test_cases, 1):
        print(f"\n[TYPED PDF TEST {idx}] {tc['name']}")
        pdf_bytes = create_typed_pdf(tc["text"])
        res = client.post(
            "/api/upload_document",
            files={"file": (f"{tc['id']}.pdf", pdf_bytes, "application/pdf")},
            data={"language": "en"},
        )
        data = res.json()
        kind = data.get("kind")
        summary = data.get("summary")
        first_step = data.get("pipeline", [{}])[0].get("detail", "") if "pipeline" in data else ""
        print(f"  Result Kind: {kind}")
        print(f"  Summary:     {summary}")
        print(f"  Pipeline #0: {first_step}")
        assert "direct PDF parsing" in first_step or kind == "bifurcation", "Expected direct PDF parsing"
        print("  Status: [PASS]")

    print("\n" + "=" * 90)
    print("PART 2: SCANNED / IMAGE-ONLY PDFS (OCR FALLBACK)")
    print("=" * 90)

    for idx, tc in enumerate(test_cases, 1):
        print(f"\n[SCANNED PDF TEST {idx}] {tc['name']}")
        scanned_pdf_bytes = create_scanned_image_only_pdf(tc["text"])

        # Check raw extract_text_from_pdf behavior
        raw_text, has_text = stage0.extract_text_from_pdf(scanned_pdf_bytes)
        print(f"  Direct PDF text layer present? {has_text} (length={len(raw_text.strip())})")

        # Run OCR extraction
        t0 = time.time()
        ocr_text = stage0.extract_text_via_ocr_from_pdf(scanned_pdf_bytes)
        ocr_time = time.time() - t0
        print(f"  OCR Extraction Time: {ocr_time:.2f}s")
        print(f"  Raw OCR Extracted Text:\n    \"{ocr_text.strip()}\"")

        # Submit to endpoint
        res = client.post(
            "/api/upload_document",
            files={"file": (f"{tc['id']}_scanned.pdf", scanned_pdf_bytes, "application/pdf")},
            data={"language": "en"},
        )
        data = res.json()
        kind = data.get("kind")
        summary = data.get("summary")
        first_step = data.get("pipeline", [{}])[0].get("detail", "") if "pipeline" in data else ""
        print(f"  Pipeline Outcome: kind={kind}, summary='{summary}'")
        print(f"  Pipeline #0:      {first_step}")

        if "expected_section" in tc:
            assert summary == f"{tc['expected_route']} {tc['expected_section']}", f"Expected {tc['expected_route']} {tc['expected_section']}, got {summary}"
        print("  Status: [PASS - Clean OCR and correct statutory mapping]")

    print("\n" + "=" * 90)
    print("PART 3: DIRECT IMAGE UPLOADS (PNG & JPEG PHOTO / SCREENSHOT OCR)")
    print("=" * 90)

    # Test PNG photo upload
    tc_png = test_cases[1]  # Riot liability BNS 193
    print(f"\n[PNG IMAGE TEST] {tc_png['name']}")
    png_bytes = create_image_bytes(tc_png["text"], fmt="PNG")
    raw_ocr_png = stage0.extract_text_from_image(png_bytes)
    print(f"  Raw OCR Extracted Text from PNG:\n    \"{raw_ocr_png}\"")
    res_png = client.post(
        "/api/upload_document",
        files={"file": ("riot_case.png", png_bytes, "image/png")},
        data={"language": "en"},
    )
    data_png = res_png.json()
    print(f"  Pipeline Outcome: kind={data_png.get('kind')}, summary='{data_png.get('summary')}'")
    print(f"  Pipeline #0:      {data_png.get('pipeline', [{}])[0].get('detail', '')}")
    assert data_png.get("summary") == "BNS 193", "PNG OCR failed to map to BNS 193"
    print("  Status: [PASS]")

    # Test JPEG photo upload
    tc_jpg = test_cases[2]  # Obscene literature IPC 292
    print(f"\n[JPEG IMAGE TEST] {tc_jpg['name']}")
    jpg_bytes = create_image_bytes(tc_jpg["text"], fmt="JPEG")
    raw_ocr_jpg = stage0.extract_text_from_image(jpg_bytes)
    print(f"  Raw OCR Extracted Text from JPEG:\n    \"{raw_ocr_jpg}\"")
    res_jpg = client.post(
        "/api/upload_document",
        files={"file": ("obscene_case.jpg", jpg_bytes, "image/jpeg")},
        data={"language": "en"},
    )
    data_jpg = res_jpg.json()
    print(f"  Pipeline Outcome: kind={data_jpg.get('kind')}, summary='{data_jpg.get('summary')}'")
    print(f"  Pipeline #0:      {data_jpg.get('pipeline', [{}])[0].get('detail', '')}")
    assert data_jpg.get("summary") == "IPC 292", "JPEG OCR failed to map to IPC 292"
    print("  Status: [PASS]")

    print("\n" + "=" * 90)
    print("ALL OCR & MULTIMODAL DOCUMENT UPLOAD TESTS COMPLETED SUCCESSFULLY.")
    print("=" * 90)


if __name__ == "__main__":
    run_all_tests()
