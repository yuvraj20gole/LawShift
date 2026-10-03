"""Re-filter Tier 1 straddling cases: drop hypotheticals and procedural-date-only.

Keyword lists are the expanded Batch-1 lists from the review prompt, not the
narrower stage1_entity_extraction.py defaults. score_context math is the same
(offense count minus procedural count, window 45).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HYPOTHETICAL_PATTERN = re.compile(
    r'\bif\s+(?:this|the\s+same)\b.{0,60}\b(?:instead|occurred|happened)\b|'
    r'\binstead\s+of\b.{0,40}\b(?:on|in)\b|'
    r'\bhad\s+(?:occurred|happened|taken\s+place)\b',
    re.IGNORECASE,
)

OFFENSE_KEYWORDS = [
    "occurred", "happened", "took place", "committed", "was attacked",
    "was killed", "was stolen", "victim", "created", "removed", "erased",
    "manufactured", "used", "sold", "reused", "possessed", "entrusted",
    "misappropriated", "colluded", "assaulted", "fabricated", "forged",
]
PROCEDURAL_KEYWORDS = [
    "filed", "filing", "fir", "registered", "statement", "report",
    "today's date", "as of", "complaint on", "recorded my statement",
    "discovered", "came to light", "brought to light", "charge sheet",
    "prosecuted", "prosecution", "trial", "investigation", "apprehended",
    "found out", "detected",
]

DATE_PATTERNS = [
    r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
]


def score_context(text, start, end, window=45):
    context = text[max(0, start - window):min(len(text), end + window)].lower()
    offense_score = sum(1 for kw in OFFENSE_KEYWORDS if kw in context)
    procedural_score = sum(1 for kw in PROCEDURAL_KEYWORDS if kw in context)
    return offense_score - procedural_score


def find_all_dates(text):
    matches = []
    seen = set()
    for pattern in DATE_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            key = (m.start(), m.end())
            if key in seen:
                continue
            seen.add(key)
            matches.append((m.group(0), m.start(), m.end()))
    matches.sort(key=lambda x: x[1])
    return matches


def main():
    with open(ROOT / "data" / "clean" / "split_offense_tier1_straddling.json") as f:
        candidates = json.load(f)

    print(f"Starting candidates: {len(candidates)}")

    filtered = []
    dropped_hypothetical = []
    dropped_procedural_only = []
    kept_lt_two_date_spans = 0

    for c in candidates:
        question = c["question"]
        row = dict(c)

        if HYPOTHETICAL_PATTERN.search(question):
            dropped_hypothetical.append(row)
            continue

        all_dates = find_all_dates(question)
        if len(all_dates) < 2:
            filtered.append(row)
            kept_lt_two_date_spans += 1
            continue

        scores = [score_context(question, s, e) for _, s, e in all_dates]
        n_positive = sum(1 for s in scores if s > 0)
        row["context_scores"] = scores
        row["date_spans"] = [d[0] for d in all_dates]
        row["n_positive_offense_context"] = n_positive

        if n_positive >= 2:
            filtered.append(row)
        else:
            dropped_procedural_only.append(row)

    print(f"\nDropped as hypothetical rephrasing: {len(dropped_hypothetical)}")
    print(
        f"Dropped as procedural-date-only (not 2 real offense dates): "
        f"{len(dropped_procedural_only)}"
    )
    print(f"Kept without dual-date span check (<2 date matches): {kept_lt_two_date_spans}")
    print(f"Remaining candidates for manual review: {len(filtered)}")

    batch1_confirmed_genuine_snippets = [
        "forging a valuable security (promissory note) on January 10, 2024",
        "removed revenue stamps from documents on June 28, 2024",
        "erased usage marks from stamps on June 29, 2024",
        "forged will was created on June 20, 2024",
    ]
    sanity = []
    print()
    for snippet in batch1_confirmed_genuine_snippets:
        survived = any(snippet in c["question"] for c in filtered)
        dropped_h = any(snippet in c["question"] for c in dropped_hypothetical)
        dropped_p = any(snippet in c["question"] for c in dropped_procedural_only)
        where = "filtered" if survived else (
            "hypothetical" if dropped_h else (
                "procedural_only" if dropped_p else "MISSING"
            )
        )
        print(f"Confirmed genuine case survived filter: {survived}  ({snippet[:50]}...) [{where}]")
        sanity.append({"snippet": snippet, "survived": survived, "where": where})

    out_filtered = ROOT / "data" / "clean" / "split_offense_tier1_filtered.json"
    with open(out_filtered, "w") as f:
        json.dump(filtered, f, indent=2)
    print(f"\nSaved to {out_filtered}")

    counts = {
        "n_starting": len(candidates),
        "n_dropped_hypothetical": len(dropped_hypothetical),
        "n_dropped_procedural_only": len(dropped_procedural_only),
        "n_kept_lt_two_date_spans": kept_lt_two_date_spans,
        "n_remaining": len(filtered),
        "batch1_confirmed_sanity": sanity,
        "filter_too_aggressive": any(not s["survived"] for s in sanity),
        "note": (
            "Filter A = hypothetical rephrasing regex on the question. "
            "Filter B = >=2 date spans in the question with net offense-context "
            "score > 0 (expanded Batch-1 keyword lists, window 45). "
            "Cases with <2 date spans kept rather than dropped."
        ),
    }
    counts_path = ROOT / "results" / "split_offense_tier1_filter_counts.json"
    with open(counts_path, "w") as f:
        json.dump(counts, f, indent=2)

    with open(ROOT / "data" / "clean" / "split_offense_tier1_dropped_hypothetical.json", "w") as f:
        json.dump(dropped_hypothetical, f, indent=2)
    with open(ROOT / "data" / "clean" / "split_offense_tier1_dropped_procedural.json", "w") as f:
        json.dump(dropped_procedural_only, f, indent=2)
    print(f"Wrote {counts_path}")


if __name__ == "__main__":
    main()
