"""Build labeled split-offense validation set and test route_with_split_detection.

Genuine-split catch rate is the real metric (n=9). Ambiguous cases are
informational only. Cases 77, 109, 116 are excluded (two separate acts,
not one continuing offense).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stage1_entity_extraction import route_with_split_detection  # noqa: E402

GENUINE_SPLIT_CASE_NUMBERS = [2, 4, 12, 18, 70, 85, 98, 146, 156]
AMBIGUOUS_CASE_NUMBERS = [14, 24, 54, 79, 123, 139]


def main(labeled_path=None, out_path=None):
    labeled_path = Path(labeled_path or ROOT / "data" / "clean" / "split_offense_labeled_validation.json")
    out_path = Path(out_path or ROOT / "results" / "split_detector_validated_eval.json")

    with open(labeled_path) as f:
        labeled_set = json.load(f)
    print(f"Labeled validation set: {len(labeled_set)} cases "
          f"({sum(1 for x in labeled_set if x['label']=='genuine_split')} genuine + "
          f"{sum(1 for x in labeled_set if x['label']=='ambiguous')} ambiguous)")
    print(f"Loaded from {labeled_path}")

    results = []
    for item in labeled_set:
        result = route_with_split_detection(item["question"])
        results.append({
            "case_number": item["case_number"],
            "label": item["label"],
            "detector_kind": result.kind,
            "detector_reason": result.reason,
            "detector_periods": result.periods,
            "detector_single_route": result.single_route,
            "correctly_flagged_as_split": result.kind == "split",
        })

    genuine_results = [r for r in results if r["label"] == "genuine_split"]
    ambiguous_results = [r for r in results if r["label"] == "ambiguous"]

    n_correct = sum(r["correctly_flagged_as_split"] for r in genuine_results)
    print(f"\nGenuine splits correctly detected: {n_correct} / {len(genuine_results)}")
    print("(This is the real, honest accuracy number - n=9, not statistically robust,")
    print(" but a real functional test rather than the earlier n=4 smoke test.)")
    for r in genuine_results:
        flag = "HIT" if r["correctly_flagged_as_split"] else "MISS"
        print(
            f"  [{flag}] Case {r['case_number']}: {r['detector_kind']} "
            f"({r['detector_reason']}) periods={r['detector_periods']}"
        )

    print("\nAmbiguous cases (informational only, no 'correct' answer):")
    for r in ambiguous_results:
        print(f"  Case {r['case_number']}: detector says {r['detector_kind']} ({r['detector_reason']})")

    out = {
        "n_genuine": len(genuine_results),
        "n_correct": n_correct,
        "accuracy_genuine": n_correct / len(genuine_results) if genuine_results else 0,
        "n_ambiguous": len(ambiguous_results),
        "n_ambiguous_flagged_split": sum(r["correctly_flagged_as_split"] for r in ambiguous_results),
        "excluded_two_separate_acts": [77, 109, 116],
        "note": (
            "Catch rate on the hand-labeled 9 genuine splits. "
            "Keyword matching is word-boundary (keyword_in_context); "
            "'use' is a standalone offense keyword."
        ),
        "genuine_results": genuine_results,
        "ambiguous_results": ambiguous_results,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument(
        "--labeled",
        default=str(ROOT / "data" / "clean" / "split_offense_labeled_validation.json"),
    )
    p.add_argument(
        "--out",
        default=str(ROOT / "results" / "split_detector_validated_eval.json"),
    )
    args = p.parse_args()
    main(args.labeled, args.out)
