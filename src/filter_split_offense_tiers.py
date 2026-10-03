"""Tier 1: cutoff-straddling multi-date cases.
Tier 2: random sample of continuing-language-only cases for FP-rate check.

Does not judge GovIntel routing correctness. Tier 2 labels (if added later)
are only 'is this actually a split/continuing temporal-jurisdiction fact pattern?'
"""
import json
import random
from datetime import date, datetime
from pathlib import Path

from dateutil import parser as dateparser

ROOT = Path(__file__).resolve().parents[1]
CUTOFF = date(2024, 7, 1)


def parse_safe(date_str):
    try:
        return dateparser.parse(
            date_str, fuzzy=True, default=datetime(2000, 1, 1)
        ).date()
    except Exception:
        return None


def main():
    with open(ROOT / "data" / "clean" / "split_offense_candidates.json") as f:
        candidates = json.load(f)

    straddling = []
    n_multi = 0
    n_multi_unparseable = 0
    for c in candidates:
        if not c["matched_multi_date"]:
            continue
        n_multi += 1
        parsed = [parse_safe(d) for d in c["dates_found_in_question"]]
        parsed = [d for d in parsed if d is not None]
        if not parsed:
            n_multi_unparseable += 1
            continue
        has_before = any(d < CUTOFF for d in parsed)
        has_after = any(d >= CUTOFF for d in parsed)
        if has_before and has_after:
            row = dict(c)
            row["parsed_dates"] = [d.isoformat() for d in sorted(set(parsed))]
            straddling.append(row)

    lang_only = [
        c for c in candidates
        if c["matched_continuing_language"] and not c["matched_multi_date"]
    ]
    random.seed(42)
    lang_sample = random.sample(lang_only, min(25, len(lang_only)))

    print(f"Multi-date candidates: {n_multi}")
    print(f"Of those, dates actually straddle the cutoff: {len(straddling)}")
    print(f"Multi-date with no parseable dates: {n_multi_unparseable}")
    print(f"\nContinuing-language-only candidates: {len(lang_only)}")
    print(f"Sampled for FP-rate check: {len(lang_sample)}")

    t1 = ROOT / "data" / "clean" / "split_offense_tier1_straddling.json"
    t2 = ROOT / "data" / "clean" / "split_offense_tier2_language_sample.json"
    with open(t1, "w") as f:
        json.dump(straddling, f, indent=2)
    with open(t2, "w") as f:
        json.dump(lang_sample, f, indent=2)

    print(f"\nTier 1 (read in full - highest precision): {len(straddling)} cases -> {t1.name}")
    print(f"Tier 2 (sample only, to estimate FP rate): {len(lang_sample)} cases -> {t2.name}")

    n_train = sum(1 for c in straddling if c["split"] == "train")
    n_eval = sum(1 for c in straddling if c["split"] == "eval")
    n_both = sum(
        1 for c in straddling
        if c["matched_continuing_language"] and c["matched_multi_date"]
    )
    counts = {
        "n_multi_date_candidates": n_multi,
        "n_multi_unparseable": n_multi_unparseable,
        "n_tier1_straddling": len(straddling),
        "n_tier1_train": n_train,
        "n_tier1_eval": n_eval,
        "n_tier1_also_continuing_language": n_both,
        "n_language_only": len(lang_only),
        "n_tier2_sample": len(lang_sample),
        "tier2_sample_seed": 42,
        "cutoff": str(CUTOFF),
        "note": (
            "Tier 1 = 2+ distinct question dates with at least one < 2024-07-01 "
            "and at least one >= 2024-07-01. Tier 2 = random sample of "
            "continuing-language-only (no multi-date signal). No routing "
            "correctness judged in this script."
        ),
    }
    counts_path = ROOT / "results" / "split_offense_tier_counts.json"
    with open(counts_path, "w") as f:
        json.dump(counts, f, indent=2)
    print(f"Wrote {counts_path}")


if __name__ == "__main__":
    main()
