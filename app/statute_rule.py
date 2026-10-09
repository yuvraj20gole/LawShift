"""Deterministic Rule text from a retrieved statute section.

Copies the main clause only after display-cleaning. Exception / Explanation /
Provided that / Illustration / STATE AMENDMENTS stay under Sources (full
section text) when a safe cut is found.

The Rule is always an exact prefix of the display-cleaned text (never
rewritten beyond the shared cleaning step).
"""
from __future__ import annotations

import re

# Leading corpus indexing prefix (same idea as frontend stripIndexingContext).
_CONTEXT_PREFIX = re.compile(r"^\[Context:[^\]]*\]\s*", re.IGNORECASE)

# Act banner on IPC rows (not part of the section body).
_ACT_HEADER = re.compile(
    r"^\s*Indian Penal Code,?\s*1860\s*\n+",
    re.IGNORECASE,
)

# Bracketed title line: "[292. Sale, etc., of obscene books, etc."
_TITLE_BRACKET = re.compile(
    r"^\[\d+[A-Za-z]{0,3}\.\s*[^\n]+\n?",
    re.MULTILINE,
)

# Short unbracketed title line before the body: "499. Defamation\nWhoever…"
# Does not match BNS lines where the body continues after an em-dash on the
# same line ("294. Sale…—(1)").
_TITLE_PLAIN = re.compile(
    r"^\d+[A-Za-z]{0,3}\.\s+[A-Z][^\n.—\-]{0,100}\n(?=[A-Z(\[])",
    re.MULTILINE,
)

# Footnote openers inserted by digitisation: "138  [" / "140  [".
_FOOTNOTE_OPEN = re.compile(r"\d+\s*\[")

# Stray footnote closers left after removing openers: "it]." → "it." / "(2)]" → "(2)".
_STRAY_BRACKET = re.compile(r"\](?=[.\s,]|$)|(?<=\))\]")

# Cut markers. Exception/Explanation are case-sensitive; STATE AMENDMENTS is not.
# Anchor: line start, after '.' / danda, after ':' + newline, or footnote open
# (digits + "[") immediately before Exception/Explanation.
_ANCILLARY_START = re.compile(
    r"(?:"
    # Always-cut block (any case), usually its own line. (?i:…) is scoped.
    r"(?:^|(?<=\n))\s*(?i:STATE\s+AMENDMENTS)\b"
    r"|"
    # Footnote-anchored Exception / Explanation (no dash required). Kept so a
    # cut still works if cleaning is skipped; after clean_statute_display the
    # Exception sits at a line/sentence anchor instead.
    r"\d+\s*\[\s*(?:Exception|Explanation)(?:\s+\d+)?\b"
    r"|"
    # Sentence / line anchored markers (capitalised; dash optional).
    r"(?:^|(?<=[.\u0964])\s*|(?<=:)\r?\n\s*)"
    r"(?:"
    r"Provided that\b"
    r"|Explanation(?:\s+\d+)?\b"
    r"|Exception(?:\s+\d+)?\b"
    r"|Illustrations?\b"
    r")"
    r")",
    re.MULTILINE,
)

_STATE_AMENDMENTS_AT = re.compile(r"(?i)STATE\s+AMENDMENTS\b")

# If a candidate cut ends on one of these, keep the full cleaned text instead
# (unless the cut is at STATE AMENDMENTS, which always applies).
_WEAK_END = re.compile(
    r"(?:"
    r"\b(?:of|the|to|a|an|and|or|by|in|for|with|under)\s*$"
    r"|[:;,]\s*$"
    r")",
    re.IGNORECASE,
)

# Audit helpers: leftover noise in a Rule.
_HAS_STATE_AMENDMENTS = re.compile(r"(?i)STATE\s+AMENDMENTS\b")
_HAS_FOOTNOTE_DIGITS_BRACKET = re.compile(r"\d+\s*\[")


def strip_context_prefix(text: str) -> str:
    """Remove a leading [Context:…] indexing prefix, if present."""
    return _CONTEXT_PREFIX.sub("", (text or "").strip()).strip()


def clean_statute_display(section_text: str) -> str:
    """Shared display cleaning for Rule text and the writer prompt.

    Removes the indexing context, act banner, leading title line, footnote
    openers like ``138  [``, and stray ``]``. Does not paraphrase or reorder
    words. Downstream Rule cuts are prefixes of this string.
    """
    text = strip_context_prefix(section_text)
    if not text:
        return ""
    text = _ACT_HEADER.sub("", text, count=1)
    text = _TITLE_BRACKET.sub("", text, count=1)
    text = _TITLE_PLAIN.sub("", text, count=1)
    text = _FOOTNOTE_OPEN.sub("", text)
    text = _STRAY_BRACKET.sub("", text)
    # Collapse whitespace left by removals, but keep newlines.
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def _ends_on_weak_token(text: str) -> bool:
    return bool(_WEAK_END.search(text or ""))


def _cut_is_state_amendments(cleaned: str, match_start: int) -> bool:
    return bool(_STATE_AMENDMENTS_AT.match(cleaned[match_start:]))


def main_clause_rule_text(section_text: str) -> str:
    """Return the main-clause statute text for the IRAC Rule field.

    Always an exact prefix of ``clean_statute_display(section_text)``.
    """
    cleaned = clean_statute_display(section_text)
    if not cleaned:
        return ""
    m = _ANCILLARY_START.search(cleaned)
    if m is None:
        return cleaned
    candidate = cleaned[: m.start()].rstrip()
    always = _cut_is_state_amendments(cleaned, m.start())
    if not always and (len(candidate) < 40 or _ends_on_weak_token(candidate)):
        return cleaned
    if always and not candidate:
        return cleaned
    return candidate


def rule_is_truncated(section_text: str, rule_text: str | None = None) -> bool:
    """True when the Rule is a proper prefix of the display-cleaned full text."""
    cleaned = clean_statute_display(section_text)
    rule = main_clause_rule_text(section_text) if rule_text is None else rule_text
    return bool(cleaned) and len(rule) < len(cleaned)


def writer_statute_text(section_text: str) -> str:
    """Full section text for the writer: display-cleaned, not main-clause-cut."""
    return clean_statute_display(section_text)


__all__ = [
    "strip_context_prefix",
    "clean_statute_display",
    "main_clause_rule_text",
    "rule_is_truncated",
    "writer_statute_text",
]
