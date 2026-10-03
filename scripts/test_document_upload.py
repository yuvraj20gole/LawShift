"""Test script for Stage 0 Document Upload endpoint regression check.

Generates typed test PDFs, runs them through POST /api/upload_document,
and compares the responses against direct POST /api/query requests.
"""
from __future__ import annotations

import io
import json
import os
import sys
import time
from pathlib import Path

from fastapi.testclient import TestClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app
import app.stage3 as stage3
import app.stage4 as stage4


def create_pdf_bytes(text: str) -> bytes:
    """Create in-memory PDF with typed text."""
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


def run_tests():
    print("=== INITIALIZING PIPELINE FOR DOCUMENT UPLOAD TEST ===")
    stage4.check_ollama()
    stage3.load()

    client = TestClient(app)

    test_cases = [
        {
            "id": "case1_bns_counterfeit",
            "name": "Case 1: Counterfeit Currency (BNS Route)",
            "text": "On 5 September 2024, a person was found in possession of counterfeit currency notes in Mumbai, knowing they were forged.",
        },
        {
            "id": "case2_bns_riot",
            "name": "Case 2: Riot Liability of Land Agent (BNS Route)",
            "text": "On 10 August 2024, a riot occurred on a property for the landowner's benefit, and the agent failed to take lawful steps to prevent it.",
        },
        {
            "id": "case3_ipc_obscene",
            "name": "Case 3: Obscene Literature Sale (IPC Route)",
            "text": "On 25 June 2024, a bookstore owner sold obscene magazines to the public for the first time.",
        },
    ]

    print("\n" + "=" * 85)
    print("RUNNING REGRESSION COMPARISON: /api/upload_document VS /api/query")
    print("=" * 85 + "\n")

    all_passed = True

    for idx, tc in enumerate(test_cases, 1):
        print(f"--- [TEST {idx}] {tc['name']} ---")
        query_text = tc["text"]
        pdf_bytes = create_pdf_bytes(query_text)

        # 1. Direct /api/query
        conv_id_query = f"test-query-{tc['id']}"
        t0 = time.time()
        res_query = client.post(
            "/api/query",
            json={"message": query_text, "conversation_id": conv_id_query, "language": "en"},
        )
        t_query = time.time() - t0
        data_query = res_query.json()

        # 2. Upload /api/upload_document
        conv_id_upload = f"test-upload-{tc['id']}"
        t0 = time.time()
        res_upload = client.post(
            "/api/upload_document",
            files={"file": (f"{tc['id']}.pdf", pdf_bytes, "application/pdf")},
            data={"language": "en", "conversation_id": conv_id_upload},
        )
        t_upload = time.time() - t0
        data_upload = res_upload.json()

        # Compare outcomes
        kind_q = data_query.get("kind")
        kind_u = data_upload.get("kind")
        summary_q = data_query.get("summary")
        summary_u = data_upload.get("summary")
        badge_q = data_query.get("badge")
        badge_u = data_upload.get("badge")

        match_kind = kind_q == kind_u
        match_summary = summary_q == summary_u
        match_badge = badge_q == badge_u

        print(f"Raw Input Text: \"{query_text}\"")
        print(f"Direct Query Response: kind={kind_q}, summary='{summary_q}', badge={badge_q}")
        print(f"Upload PDF Response:   kind={kind_u}, summary='{summary_u}', badge={badge_u}")
        print(f"Timing: /api/query={t_query:.2f}s | /api/upload_document={t_upload:.2f}s")

        if match_kind and match_summary and match_badge:
            print(">>> REGRESSION CHECK RESULT: [PASS] Identical statutory section & route.")
        else:
            print(">>> REGRESSION CHECK RESULT: [FAIL] Output mismatch between upload and query!")
            all_passed = False

        print()

    # Test Scanned/Empty PDF handling
    print("--- [TEST 4] Edge Case: Scanned/Empty PDF (<50 chars) ---")
    empty_pdf = create_pdf_bytes("Short text")
    res_empty = client.post(
        "/api/upload_document",
        files={"file": ("scanned.pdf", empty_pdf, "application/pdf")},
    )
    data_empty = res_empty.json()
    print("Response for scanned/empty PDF:", json.dumps(data_empty, indent=2))
    if data_empty.get("kind") == "failure" and data_empty.get("reason") == "source_unavailable":
        print(">>> SCANNED/EMPTY PDF CHECK: [PASS] Correctly flagged for OCR requirement.")
    else:
        print(">>> SCANNED/EMPTY PDF CHECK: [FAIL] Unexpected response.")
        all_passed = False

    # Test Non-PDF rejection
    print("\n--- [TEST 5] Edge Case: Unsupported File Type (.txt) ---")
    res_txt = client.post(
        "/api/upload_document",
        files={"file": ("test.txt", b"plain text", "text/plain")},
    )
    data_txt = res_txt.json()
    print("Response for non-PDF:", json.dumps(data_txt, indent=2))
    if data_txt.get("kind") == "failure" and "Unsupported file type" in data_txt.get("message", ""):
        print(">>> FILE TYPE CHECK: [PASS] Correctly rejected unsupported file type.")
    else:
        print(">>> FILE TYPE CHECK: [FAIL] Unexpected response.")
        all_passed = False

    print("\n" + "=" * 85)
    if all_passed:
        print("ALL DOCUMENT UPLOAD REGRESSION AND EDGE-CASE TESTS PASSED.")
    else:
        print("SOME TESTS FAILED.")
    print("=" * 85)


if __name__ == "__main__":
    run_tests()
