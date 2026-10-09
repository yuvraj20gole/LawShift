"""Deterministic Rule text from a retrieved statute section.

Copies the main clause only. Exception / Explanation / Provided that /
Illustration blocks stay under Sources (full section text) when a safe cut
is found.
"""
from __future__ import annotations

import re

# Leading corpus indexing prefix (same idea as frontend stripIndexingContext).
_CONTEXT_PREFIX = re.compile(r"^\[Context:[^\]]*\]\s*", re.IGNORECASE)

# Cut only at anchored, capitalised Bare Act markers — never mid-sentence.
# Anchor: line start, or after '.' / danda, or after ':' immediately followed
# by a newline. Marker match is case-sensitive.
_ANCILLARY_START = re.compile(
    # Anchor: start of string/line, after '.' or danda, or after ':' + newline.
    # Do not treat a bare space as a sentence end (that would cut mid-clause).
    r"(?:^|(?<=[.\u0964])\s*|(?<=:)\r?\n\s*)"
    r"(?:"
    r"Provided that\b"
    r"|Explanation(?:\s+\d+)?\s*[.—\-]"
    r"|Exception(?:\s+\d+)?\s*[.—\-]"
    r"|Illustrations?\b"
    r")",
    re.MULTILINE,
)

# If a candidate cut ends on one of these, keep the full cleaned text instead.
_WEAK_END = re.compile(
    r"(?:"
    r"\b(?:of|the|to|a|an|and|or|by|in|for|with|under)\s*$"
    r"|[:;,]\s*$"
    r")",
    re.IGNORECASE,
)


def strip_context_prefix(text: str) -> str:
    """Remove a leading [Context:…] indexing prefix, if present."""
    return _CONTEXT_PREFIX.sub("", (text or "").strip()).strip()


def _ends_on_weak_token(text: str) -> bool:
    return bool(_WEAK_END.search(text or ""))


def main_clause_rule_text(section_text: str) -> str:
    """Return the main-clause statute text for the IRAC Rule field.

    The result is always an exact prefix of the cleaned section text (verbatim
    copy; never rewritten). Unsafe cuts (too short, or ending on a weak token)
    fall back to the full cleaned text.
    """
    cleaned = strip_context_prefix(section_text)
    if not cleaned:
        return ""
    m = _ANCILLARY_START.search(cleaned)
    if m is None:
        return cleaned
    candidate = cleaned[: m.start()].rstrip()
    if len(candidate) < 40 or _ends_on_weak_token(candidate):
        return cleaned
    return candidate


def rule_is_truncated(section_text: str, rule_text: str | None = None) -> bool:
    """True when the Rule is a proper prefix of the cleaned full section text."""
    cleaned = strip_context_prefix(section_text)
    rule = main_clause_rule_text(section_text) if rule_text is None else rule_text
    return bool(cleaned) and len(rule) < len(cleaned)


__all__ = [
    "strip_context_prefix",
    "main_clause_rule_text",
    "rule_is_truncated",
]
