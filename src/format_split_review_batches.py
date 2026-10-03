"""Format Tier 1 straddling cases into markdown review batches of 20."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_SIZE = 20


def main():
    with open(ROOT / "data" / "clean" / "split_offense_tier1_straddling.json") as f:
        cases = json.load(f)

    print(f"Total cases: {len(cases)}")
    n_batches = (len(cases) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_num in range(n_batches):
        start = batch_num * BATCH_SIZE
        end = min(start + BATCH_SIZE, len(cases))
        batch = cases[start:end]
        out_path = ROOT / "results" / f"split_review_batch_{batch_num + 1}.md"

        with open(out_path, "w") as f:
            f.write(
                f"# Split-Offense Review — Batch {batch_num + 1} "
                f"({start + 1}-{end} of {len(cases)})\n\n"
            )
            f.write("For each case, judge:\n")
            f.write(
                "1. Is this GENUINELY a split/continuing-offense case "
                "(real conduct straddling 1 July 2024), or a false positive "
                "(e.g. two unrelated dates, one procedural)?\n"
            )
            f.write(
                "2. If genuine: does the correct answer need TWO periods "
                "(IPC for early acts, BNS for later/continuing acts), or does "
                "it actually resolve to ONE law despite having two dates?\n"
            )
            f.write(
                "3. Note if GovIntel's own reply is internally inconsistent "
                "or self-corrects (as seen in Case 3/4 before) — don't treat "
                "their answer as automatic gold truth.\n\n---\n\n"
            )

            for i, case in enumerate(batch):
                f.write(f"## Case {start + i + 1}\n\n")
                split = case.get("split", "?")
                f.write(f"**Split:** {split}\n\n")
                dates = case.get("dates_found_in_question") or []
                f.write(f"**Dates found in question:** {', '.join(dates)}\n\n")
                parsed = case.get("parsed_dates")
                if parsed:
                    f.write(f"**Parsed dates:** {', '.join(parsed)}\n\n")
                f.write(f"**Question:**\n{case['question']}\n\n")
                f.write(f"**Assistant reply:**\n{case['assistant_reply']}\n\n")
                f.write(
                    "**Judgment:** [ ] Genuine split (2 periods)  "
                    "[ ] Genuine but single law  [ ] False positive  "
                    "[ ] Ambiguous/inconsistent\n\n"
                )
                f.write("---\n\n")

        print(f"Batch {batch_num + 1}: cases {start + 1}-{end} -> {out_path.name}")

    print(
        f"\n{n_batches} batches created, {BATCH_SIZE} cases each "
        f"(last batch may be smaller)"
    )


if __name__ == "__main__":
    main()
