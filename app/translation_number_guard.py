"""Pure number-preservation checks for Stage 5 HI/MR translation.

After a field is machine-translated, compare digit multisets (ASCII + Devanagari
normalised to ASCII). If they differ, callers keep the English text for that
field.

List markers (short enumerated labels) are ignored so "(1)" / "2." do not
force a fallback when the translator drops or reformats a list. A digit
sequence is treated as a list marker only when ALL of:

- it is at most two digits long; and
- it matches ``(n)`` not immediately after a section keyword, or
  ``n.`` / ``n)`` at the start of a line (or after a newline); and
- the preceding ~24 characters do not contain a section cue
  (section / IPC / BNS / BNSS / BSA / धारा / कलम / §).

Section-number drift is reported separately by comparing section-reference
captures (Section/IPC/BNS/…/धारा/कलम/§ + digits), not the full digit bag.
"""
from __future__ import annotations

import re
from collections import Counter

_DEVANAGARI_TO_ASCII = str.maketrans("०१२३४५६७८९", "0123456789")

_DIGIT_SPAN = re.compile(r"\d+")

# Section / statute cues then a number (ASCII digits after normalisation).
_SECTION_REF = re.compile(
    r"(?i)(?:sections?|ipc|bns|bnss|bsa|धारा|कलम|कलमे)\s*[./-]?\s*(\d+)"
    r"|§\s*(\d+)"
)

_SECTION_CUES = (
    "section",
    "sections",
    "ipc",
    "bns",
    "bnss",
    "bsa",
    "धारा",
    "कलम",
    "कलमे",
    "§",
)


def ascii_normalize_digits(text: str) -> str:
    """Map Devanagari digits to ASCII; leave other characters unchanged."""
    return (text or "").translate(_DEVANAGARI_TO_ASCII)


def _preceded_by_section_cue(text: str, start: int, window: int = 24) -> bool:
    pre = text[max(0, start - window) : start].lower()
    return any(cue in pre for cue in _SECTION_CUES)


def list_marker_spans(text: str) -> set[tuple[int, int]]:
    """Character spans (start, end) of digit runs that are list markers only."""
    t = ascii_normalize_digits(text)
    spans: set[tuple[int, int]] = set()

    # Parenthetical enumerations: (1) (12)
    for m in re.finditer(r"(?<!\d)\((\d{1,2})\)(?!\d)", t):
        if _preceded_by_section_cue(t, m.start()):
            continue
        spans.add((m.start(1), m.end(1)))

    # Line-leading "1." / "2)" (after start or newline)
    for m in re.finditer(r"(?:^|\n)\s*(\d{1,2})[.)]\s", t):
        if _preceded_by_section_cue(t, m.start(1)):
            continue
        spans.add((m.start(1), m.end(1)))

    return spans


def extract_digit_multiset(text: str) -> Counter[str]:
    """Multiset of digit sequences, excluding recognised list markers."""
    t = ascii_normalize_digits(text)
    markers = list_marker_spans(text)
    counts: Counter[str] = Counter()
    for m in _DIGIT_SPAN.finditer(t):
        if (m.start(), m.end()) in markers:
            continue
        counts[m.group()] += 1
    return counts


def extract_section_numbers(text: str) -> Counter[str]:
    """Multiset of numbers tied to section / statute references."""
    t = ascii_normalize_digits(text)
    counts: Counter[str] = Counter()
    for m in _SECTION_REF.finditer(t):
        n = m.group(1) or m.group(2)
        if n:
            counts[n] += 1
    return counts


def numbers_match(english: str, translated: str) -> bool:
    return extract_digit_multiset(english) == extract_digit_multiset(translated)


def section_numbers_changed(english: str, translated: str) -> bool:
    return extract_section_numbers(english) != extract_section_numbers(translated)


def digit_diff_examples(english: str, translated: str) -> dict[str, list[str]]:
    """Return only the differing number tokens (no surrounding text)."""
    en = extract_digit_multiset(english)
    tr = extract_digit_multiset(translated)
    only_en: list[str] = []
    only_tr: list[str] = []
    for n, c in sorted(en.items()):
        d = c - tr.get(n, 0)
        if d > 0:
            only_en.extend([n] * d)
    for n, c in sorted(tr.items()):
        d = c - en.get(n, 0)
        if d > 0:
            only_tr.extend([n] * d)
    return {"english_only": only_en, "translated_only": only_tr}


def guard_translated_field(english: str, translated: str) -> tuple[str, bool]:
    """If digit multisets differ, keep English and report fallback.

    Returns (text_to_use, fell_back).
    """
    if not isinstance(english, str):
        english = "" if english is None else str(english)
    if not isinstance(translated, str):
        translated = "" if translated is None else str(translated)
    if numbers_match(english, translated):
        return translated, False
    return english, True


def apply_number_guard(
    english_irac: dict,
    translated_irac: dict,
    fields: tuple[str, ...] = ("issue", "rule", "application"),
) -> tuple[dict, list[str]]:
    """Guard selected fields; return (merged_irac, fallback_field_names)."""
    out = dict(translated_irac)
    fallback: list[str] = []
    for key in fields:
        if key not in english_irac:
            continue
        en = english_irac.get(key) or ""
        tr = translated_irac.get(key) or ""
        if not isinstance(en, str) or not isinstance(tr, str):
            continue
        text, fell = guard_translated_field(en, tr)
        out[key] = text
        if fell:
            fallback.append(key)
    return out, fallback


__all__ = [
    "ascii_normalize_digits",
    "extract_digit_multiset",
    "extract_section_numbers",
    "numbers_match",
    "section_numbers_changed",
    "digit_diff_examples",
    "guard_translated_field",
    "apply_number_guard",
    "list_marker_spans",
]
