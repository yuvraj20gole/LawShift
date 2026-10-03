"""Realistic Document Degradation & OCR Robustness Test Suite.

Simulates physical page conditions, camera capture artifacts, lighting variations,
geometric distortions, and character-level digit/spelling vulnerabilities to test
whether degraded OCR causes silent date misparsing or graceful fallbacks.
"""
from __future__ import annotations

import io
import json
import math
import os
import random
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app
import app.stage0_document as stage0
import app.stage1 as stage1
import app.stage3 as stage3
import app.stage4 as stage4


def render_base_document(
    text: str,
    font_name: str = "Times",
    font_size: int = 34,
    doc_width: int = 1400,
    doc_height: int = 700,
    bg_color: tuple[int, int, int] = (248, 246, 240),  # realistic off-white paper
) -> Image.Image:
    """Render crisp document text onto an off-white simulated paper canvas."""
    img = Image.new("RGB", (doc_width, doc_height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Try standard system serif/sans fonts
    font = None
    candidate_fonts = [
        f"/System/Library/Fonts/Supplemental/{font_name}.ttf",
        f"/System/Library/Fonts/{font_name}.ttc",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for p in candidate_fonts:
        if os.path.exists(p):
            try:
                font = ImageFont.truetype(p, font_size)
                break
            except Exception:
                pass
    if font is None:
        font = ImageFont.load_default()

    words = text.split(" ")
    lines = []
    curr: list[str] = []
    for w in words:
        curr.append(w)
        if len(" ".join(curr)) > 55:
            lines.append(" ".join(curr))
            curr = []
    if curr:
        lines.append(" ".join(curr))

    y = 120
    for line in lines:
        draw.text((120, y), line, fill=(25, 25, 30), font=font)
        y += font_size + 18

    return img


def apply_lighting_gradient(img: Image.Image, intensity: float = 0.45) -> Image.Image:
    """Simulate uneven phone camera illumination (e.g. shadow from top or side)."""
    arr = np.array(img, dtype=np.float32)
    h, w, _ = arr.shape
    # Diagonal gradient (top-left lighter, bottom-right shadowed)
    y_grad = np.linspace(1.0, 1.0 - intensity, h)[:, None]
    x_grad = np.linspace(1.0, 1.0 - (intensity * 0.7), w)[None, :]
    gradient = y_grad * x_grad
    arr = arr * gradient[:, :, None]
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def apply_perspective_and_rotation(
    img: Image.Image, angle_deg: float = 3.0, perspective_factor: float = 0.05
) -> Image.Image:
    """Simulate photo taken at an angle with slight page rotation."""
    # 1. Rotation with expansion
    rotated = img.rotate(angle_deg, resample=Image.BICUBIC, expand=True, fillcolor=(240, 238, 230))

    # 2. Perspective warp using PIL transform
    w, h = rotated.size
    dx = int(w * perspective_factor)
    dy = int(h * perspective_factor)
    coeffs = (
        1 - perspective_factor, 0.01, 0,
        0.01, 1 - (perspective_factor * 0.5), 0,
        0.0001, 0.00005
    )
    # Simple affine quad mesh warp
    transformed = rotated.transform(
        (w, h),
        Image.PERSPECTIVE,
        coeffs,
        Image.BICUBIC,
        fillcolor=(235, 232, 224),
    )
    return transformed


def apply_sensor_noise_and_blur(
    img: Image.Image, noise_sigma: float = 12.0, blur_radius: float = 0.8
) -> Image.Image:
    """Simulate camera sensor noise, imperfect focus, and low-contrast paper grain."""
    # Gaussian blur for slight lens softness
    if blur_radius > 0:
        img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    # Additive Gaussian noise
    arr = np.array(img, dtype=np.float32)
    noise = np.random.normal(0, noise_sigma, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    noisy_img = Image.fromarray(arr)

    # Reduced contrast
    enhancer = ImageEnhance.Contrast(noisy_img)
    noisy_img = enhancer.enhance(0.78)

    return noisy_img


def degrade_document(
    text: str,
    font_name: str = "Times",
    angle_deg: float = 2.5,
    lighting_intensity: float = 0.35,
    noise_sigma: float = 14.0,
    blur_radius: float = 0.7,
    jpeg_quality: int = 70,
) -> tuple[Image.Image, bytes]:
    """Combine realistic physical capture artifacts into a single simulated photo."""
    base = render_base_document(text, font_name=font_name)
    lit = apply_lighting_gradient(base, intensity=lighting_intensity)
    warped = apply_perspective_and_rotation(lit, angle_deg=angle_deg)
    final_img = apply_sensor_noise_and_blur(warped, noise_sigma=noise_sigma, blur_radius=blur_radius)

    # Compress to JPEG bytes (simulating phone camera compression)
    buf = io.BytesIO()
    final_img.save(buf, format="JPEG", quality=jpeg_quality)
    jpeg_bytes = buf.getvalue()
    return final_img, jpeg_bytes


def run_realistic_ocr_suite():
    print("=" * 95)
    print("REALISTIC DOCUMENT DEGRADATION & OCR ROBUSTNESS EVALUATION")
    print("=" * 95)

    stage4.check_ollama()
    stage3.load()
    client = TestClient(app)

    # Define diverse, challenging test scenarios
    scenarios = [
        {
            "id": "scenario_1_phone_photo_bns_riot",
            "name": "Scenario 1: Phone Photo of Printed Page (BNS 193 Riot Liability)",
            "text": "On 10 August 2024, a riot occurred on a property for the landowner's benefit, and the agent failed to take lawful steps to prevent it.",
            "true_date": date(2024, 8, 10),
            "expected_act": "BNS",
            "expected_section": "193",
            "font": "Times",
            "angle": 3.2,
            "lighting": 0.40,
            "noise": 15.0,
            "blur": 0.6,
            "quality": 70,
        },
        {
            "id": "scenario_2_faded_paper_ipc_obscene",
            "name": "Scenario 2: Low-Contrast Faded Document (IPC 292 Obscene Literature)",
            "text": "On 25 June 2024, a bookstore owner sold obscene magazines to the public for the first time.",
            "true_date": date(2024, 6, 25),
            "expected_act": "IPC",
            "expected_section": "292",
            "font": "Courier New",
            "angle": -2.8,
            "lighting": 0.35,
            "noise": 18.0,
            "blur": 0.8,
            "quality": 65,
        },
        {
            "id": "scenario_3_digit_vulnerability_bns_counterfeit",
            "name": "Scenario 3: Single-Digit Month/Day & Shadow Gradient (BNS 180 Counterfeit)",
            "text": "On 5 September 2024, a person was found in possession of counterfeit currency notes in Mumbai, knowing they were forged.",
            "true_date": date(2024, 9, 5),
            "expected_act": "BNS",
            "expected_section": None,  # bifurcates to 178/179/180
            "font": "Times",
            "angle": 4.1,
            "lighting": 0.50,
            "noise": 16.0,
            "blur": 0.9,
            "quality": 60,
        },
        {
            "id": "scenario_4_severe_motion_noise_probe",
            "name": "Scenario 4: High-Noise / Heavy-Blur Stress Probe (Cutoff Boundary Date 01 July 2024)",
            "text": "On 1 July 2024, an incident occurred where stolen goods were knowingly received and concealed.",
            "true_date": date(2024, 7, 1),
            "expected_act": "BNS",
            "font": "Helvetica",
            "angle": -4.5,
            "lighting": 0.55,
            "noise": 25.0,
            "blur": 1.4,
            "quality": 50,
        },
    ]

    results_summary = []

    for idx, sc in enumerate(scenarios, 1):
        print(f"\n[{'#' * 30} TEST {idx}: {sc['name']} {'#' * 30}]")
        print(f"Ground Truth Text:\n  \"{sc['text']}\"")
        print(f"Ground Truth Date: {sc['true_date']} -> Route: {sc['expected_act']}")
        print(f"Degradation Parameters: Angle={sc['angle']}°, Lighting={sc['lighting']}, Noise σ={sc['noise']}, Blur={sc['blur']}, JPEG Q={sc['quality']}")

        # Generate realistic degraded document
        np.random.seed(42 + idx)
        random.seed(42 + idx)
        img, jpeg_bytes = degrade_document(
            text=sc["text"],
            font_name=sc["font"],
            angle_deg=sc["angle"],
            lighting_intensity=sc["lighting"],
            noise_sigma=sc["noise"],
            blur_radius=sc["blur"],
            jpeg_quality=sc["quality"],
        )

        # 1. OCR Extraction
        t0 = time.time()
        raw_ocr_text = stage0.extract_text_from_image(jpeg_bytes)
        ocr_elapsed = time.time() - t0

        print("\n--- RAW OCR OUTPUT (Character-for-Character) ---")
        print(f"\"\"\"\n{raw_ocr_text}\n\"\"\"")
        print(f"[OCR extraction took: {ocr_elapsed:.2f}s]")

        # 2. Stage 1 Offense Date Extraction from OCR text
        parsed_date, matched_text, reason = stage1.extract_offense_date(raw_ocr_text)
        print("\n--- STAGE 1 DATE EXTRACTION ANALYSIS ---")
        print(f"  Matched Date Text : '{matched_text}'")
        print(f"  Parsed Date Object: {parsed_date}")
        print(f"  Extraction Reason : {reason}")

        # Classify Date Fidelity
        date_status = "UNKNOWN"
        is_exact_date = (parsed_date == sc["true_date"])
        is_silent_corruption = False

        if is_exact_date:
            date_status = "EXACT_MATCH"
            print("  Date Fidelity     : [SAFE / EXACT MATCH] True date accurately recovered from noisy OCR.")
        elif parsed_date is None:
            date_status = "SAFE_FALLBACK_CLARIFY"
            print("  Date Fidelity     : [SAFE FALLBACK] OCR degraded date span; pipeline cleanly flagged no_date/ambiguous instead of guessing.")
        else:
            # Dangerous case: parsed a valid date, but WRONG calendar date!
            date_status = "CRITICAL_SILENT_CORRUPTION"
            is_silent_corruption = True
            print(f"  Date Fidelity     : [CRITICAL DANGER: SILENT DATE CORRUPTION!]")
            print(f"                      True Date: {sc['true_date']} vs Corrupted OCR Date: {parsed_date}")

        # 3. Full FastAPI Pipeline Execution
        print("\n--- FULL PIPELINE EXECUTION (/api/upload_document) ---")
        conv_id = f"test-ocr-degraded-{sc['id']}"
        t_pipe = time.time()
        res = client.post(
            "/api/upload_document",
            files={"file": (f"{sc['id']}.jpg", jpeg_bytes, "image/jpeg")},
            data={"language": "en", "conversation_id": conv_id},
        )
        pipe_elapsed = time.time() - t_pipe
        data = res.json()

        kind = data.get("kind")
        summary = data.get("summary")
        badge = data.get("badge")
        pipeline_steps = [s.get("detail") for s in data.get("pipeline", [])]

        print(f"  HTTP Response Kind: {kind}")
        print(f"  Statutory Summary : {summary}")
        print(f"  Badge             : {badge}")
        print(f"  Pipeline Steps    : {pipeline_steps}")

        results_summary.append({
            "test_no": idx,
            "name": sc["name"],
            "true_date": str(sc["true_date"]),
            "parsed_date": str(parsed_date) if parsed_date else None,
            "matched_text": matched_text,
            "date_status": date_status,
            "silent_corruption": is_silent_corruption,
            "pipeline_kind": kind,
            "statutory_summary": summary,
        })

    print("\n" + "=" * 95)
    print("DEGRADED OCR ROBUSTNESS SUMMARY MATRIX")
    print("=" * 95)
    print(f"{'Test':<6} | {'True Date':<11} | {'OCR Matched Date':<18} | {'Date Status':<28} | {'Pipeline Outcome'}")
    print("-" * 95)
    for r in results_summary:
        print(f"#{r['test_no']:<5} | {r['true_date']:<11} | {str(r['matched_text']):<18} | {r['date_status']:<28} | {r['pipeline_kind']} ({r['statutory_summary']})")
    print("=" * 95)


if __name__ == "__main__":
    run_realistic_ocr_suite()
