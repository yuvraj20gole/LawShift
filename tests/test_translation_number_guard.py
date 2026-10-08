"""Unit tests for app.translation_number_guard (no model, no network)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.translation_number_guard import (
    apply_number_guard,
    digit_diff_examples,
    extract_digit_multiset,
    extract_section_numbers,
    guard_translated_field,
    list_marker_spans,
    numbers_match,
    section_numbers_changed,
)


def test_devanagari_normalised_equal():
    en = "Section 302 applies on 25 June 2024."
    hi = "धारा ३०२ २५ जून २०२४ को लागू होती है।"
    assert numbers_match(en, hi)
    assert not section_numbers_changed(en, hi)


def test_section_302_to_307_detected():
    en = "The facts engage Section 302 of the IPC."
    hi = "तथ्य धारा 307 IPC के अंतर्गत आते हैं।"
    assert not numbers_match(en, hi)
    assert section_numbers_changed(en, hi)
    text, fell = guard_translated_field(en, hi)
    assert fell and text == en
    diff = digit_diff_examples(en, hi)
    assert "302" in diff["english_only"]
    assert "307" in diff["translated_only"]


def test_list_markers_ignored():
    en = "(1) First point. (2) Second about Section 292."
    # Translator drops list markers but keeps 292
    tr = "पहले बिंदु। दूसरे में Section 292।"
    assert "292" in extract_digit_multiset(en)
    assert numbers_match(en, tr)
    assert list_marker_spans(en)  # (1) and (2) marked


def test_line_leading_list_markers_ignored():
    en = "1. Sale of books.\n2. Under IPC 292."
    tr = "पुस्तकों की बिक्री।\nIPC 292 के अंतर्गत।"
    assert numbers_match(en, tr)


def test_section_cue_not_treated_as_list_marker():
    # "(302)" after section cue must count
    en = "See IPC (302) for punishment."
    tr = "सज़ा के लिए IPC (307) देखें।"
    assert not numbers_match(en, tr)


def test_year_and_amount_preserved():
    en = "Fine may extend to 2000 rupees from 1 July 2024."
    tr = "जुर्माना 1 जुलाई 2024 से 2000 रुपये तक।"
    assert numbers_match(en, tr)


def test_apply_number_guard_partial():
    en = {
        "issue": "Does Section 302 apply?",
        "rule": "Whoever commits murder…",
        "application": "This is Section 302.",
        "conclusion": "Falls within IPC 302.",
    }
    tr = {
        "issue": "क्या धारा 307 लागू?",
        "rule": "Whoever commits murder…",
        "application": "यह धारा 302 है।",
        "conclusion": "IPC 302 के अंतर्गत।",
    }
    out, fb = apply_number_guard(en, tr)
    assert fb == ["issue"]
    assert out["issue"] == en["issue"]
    assert out["application"] == tr["application"]


def test_extract_section_numbers_codes():
    text = "IPC 302 and BNS 103; धारा 292"
    assert extract_section_numbers(text) == {"302": 1, "103": 1, "292": 1}


if __name__ == "__main__":
    test_devanagari_normalised_equal()
    test_section_302_to_307_detected()
    test_list_markers_ignored()
    test_line_leading_list_markers_ignored()
    test_section_cue_not_treated_as_list_marker()
    test_year_and_amount_preserved()
    test_apply_number_guard_partial()
    test_extract_section_numbers_codes()
    print("all passed")
