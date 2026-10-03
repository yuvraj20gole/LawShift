"""Stage 4: larger gold-chunk IRAC sample for manual review.

Oversamples `exceptions` (20) plus 20 other types. Does not auto-judge
Rule–Conclusion consistency — that needs a human reader.

Requires Ollama with qwen2.5:3b-instruct (see src/stage4_generate.py).

Outputs:
  results/stage4_larger_sample.json
  results/stage4_review.md
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage4_generate import check_ollama, generate_irac

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

JSON_OUT = RESULTS / "stage4_larger_sample.json"
MD_OUT = RESULTS / "stage4_review.md"

N_EXCEPTIONS = 20
N_OTHER = 20
SEED = 42


def as_blockquote(text: str) -> str:
    lines = (text or "").strip().splitlines() or [""]
    return "\n".join(f"> {line}" if line else ">" for line in lines)


def write_review_md(results: list) -> None:
    n = len(results)
    n_exc = sum(1 for r in results if r["question_type"] == "exceptions")
    n_other = n - n_exc
    type_counts = (
        pd.Series([r["question_type"] for r in results]).value_counts().to_string()
        if results
        else "(none)"
    )
    with MD_OUT.open("w") as f:
        f.write(f"# Stage 4 Generation Review — {n} gold-chunk cases\n\n")
        f.write(
            f"Gold retrieved chunk only (no cascade). Sample: {n_exc} exceptions "
            f"+ {n_other} other types (seed={SEED}).\n\n"
        )
        f.write("**Question-type mix in this file:**\n\n```\n")
        f.write(type_counts)
        f.write("\n```\n\n")
        f.write("For each case, judge:\n")
        f.write(
            "1. Is the Rule section accurately drawn from the retrieved text (grounded)?\n"
        )
        f.write(
            "2. Does the Conclusion actually follow from the Rule and Application, "
            "or does it contradict/ignore them (as in the earlier Case 5)?\n"
        )
        f.write(
            "3. Any fabricated fact, section, or citation not in the retrieved text?\n\n"
        )
        f.write("---\n\n")
        for r in results:
            f.write(f"## Case {r['case_number']} — {r['question_type']}\n\n")
            f.write(f"**Chunk:** `{r['chunk_id']}`\n\n")
            f.write(f"**Question:** {r['question']}\n\n")
            f.write(f"**Retrieved text ({r['chunk_id']}):**\n")
            f.write(as_blockquote(r["retrieved_text"]))
            f.write("\n\n")
            f.write("**Reference answer:**\n")
            f.write(as_blockquote(str(r.get("reference_answer") or "")))
            f.write("\n\n")
            f.write("**Generated IRAC:**\n\n")
            f.write(r["generated_irac"].strip())
            f.write("\n\n")
            f.write(
                "**Judgment:** [ ] Grounded & consistent  "
                "[ ] Grounded but Rule/Conclusion mismatch (Case-5-style)  "
                "[ ] Fabricated content  "
                "[ ] Other issue\n\n"
            )
            f.write("---\n\n")


def save(results: list) -> None:
    RESULTS.mkdir(exist_ok=True)
    with JSON_OUT.open("w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    write_review_md(results)


def main():
    check_ollama()

    statutes = pd.read_json(ROOT / "data/clean/statutes.jsonl", lines=True)
    statutes_lookup = dict(zip(statutes["chunk_id"], statutes["text"]))
    test_set = pd.read_json(ROOT / "data/splits/test.jsonl", lines=True)

    print("Test set question_type distribution:")
    print(test_set["question_type"].value_counts())

    exceptions_cases = test_set[test_set["question_type"] == "exceptions"]
    n_exceptions = min(N_EXCEPTIONS, len(exceptions_cases))
    exceptions_sample = exceptions_cases.sample(n_exceptions, random_state=SEED)

    other_cases = test_set[test_set["question_type"] != "exceptions"]
    other_sample = other_cases.sample(min(N_OTHER, len(other_cases)), random_state=SEED)

    sample = pd.concat([exceptions_sample, other_sample]).reset_index(drop=True)
    print(
        f"\nTotal sample: {len(sample)} "
        f"({n_exceptions} exceptions + {len(other_sample)} other types)"
    )
    print("\nSample mix:")
    print(sample["question_type"].value_counts())

    results = []
    for i, row in sample.iterrows():
        retrieved = statutes_lookup.get(row["chunk_id"], "")
        if not retrieved:
            print(f"WARNING: chunk_id {row['chunk_id']} missing — skipping")
            continue
        print(
            f"  generating {i + 1}/{len(sample)}  "
            f"{row['chunk_id']}  ({row['question_type']})..."
        )
        output = generate_irac(row["question"], retrieved, row["chunk_id"])
        results.append(
            {
                "case_number": int(i) + 1,
                "question_type": row["question_type"],
                "chunk_id": row["chunk_id"],
                "question": row["question"],
                "retrieved_text": retrieved,
                "reference_answer": row.get("answer", ""),
                "generated_irac": output,
            }
        )
        save(results)
        if (i + 1) % 5 == 0:
            print(f"  {i + 1}/{len(sample)} done...")

    print(f"\nSaved {len(results)} cases to {JSON_OUT}")
    print(f"Review file: {MD_OUT}")


if __name__ == "__main__":
    main()
