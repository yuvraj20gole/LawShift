"""Mine GovIntel train+eval for continuing / split-offense candidate cases.

Counts and candidate dump only. Does not judge routing correctness.
"""
import json
import re
from pathlib import Path

from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[1]

CONTINUING_LANGUAGE = re.compile(
    r'\bcontinu(?:ing|ed|ance)\b|\bpersist(?:ed|ing)\b|\bongoing\b|'
    r'\bspans?\b.{0,30}\bJuly\b|\bstraddl',
    re.IGNORECASE,
)

DATE_PATTERN = re.compile(
    r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b|'
    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
    re.IGNORECASE,
)


def load_jsonl(repo_file):
    path = hf_hub_download(
        "aashnasharma/govintel-legal-dataset",
        repo_file,
        repo_type="dataset",
    )
    with open(path) as f:
        return [json.loads(l) for l in f]


def main():
    train_lines = load_jsonl("data/train.jsonl")
    eval_lines = load_jsonl("data/eval.jsonl")
    all_lines = (
        [{"split": "train", **r} for r in train_lines]
        + [{"split": "eval", **r} for r in eval_lines]
    )
    print(f"Total combined rows: {len(all_lines)}")

    candidates = []
    n_no_messages = 0
    for record in all_lines:
        messages = record.get("messages", [])
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
        assistant_msg = next((m["content"] for m in messages if m["role"] == "assistant"), None)
        if not user_msg or not assistant_msg:
            n_no_messages += 1
            continue

        dates_in_question = DATE_PATTERN.findall(user_msg)
        has_continuing_language = bool(
            CONTINUING_LANGUAGE.search(user_msg) or CONTINUING_LANGUAGE.search(assistant_msg)
        )
        has_multi_date_question = len(set(dates_in_question)) >= 2

        if has_continuing_language or has_multi_date_question:
            candidates.append({
                "split": record["split"],
                "question": user_msg,
                "assistant_reply": assistant_msg,
                "matched_continuing_language": has_continuing_language,
                "matched_multi_date": has_multi_date_question,
                "dates_found_in_question": sorted(set(dates_in_question)),
            })

    n_cont = sum(1 for c in candidates if c["matched_continuing_language"])
    n_multi = sum(1 for c in candidates if c["matched_multi_date"])
    n_both = sum(
        1 for c in candidates
        if c["matched_continuing_language"] and c["matched_multi_date"]
    )
    n_train = sum(1 for c in candidates if c["split"] == "train")
    n_eval = sum(1 for c in candidates if c["split"] == "eval")

    print(f"\nSkipped (no user/assistant): {n_no_messages}")
    print(f"\nTotal candidates found: {len(candidates)}")
    print(f"  Via continuing-offense language: {n_cont}")
    print(f"  Via 2+ dates in question: {n_multi}")
    print(f"  Via both signals: {n_both}")
    print(f"  From train split: {n_train}")
    print(f"  From eval split: {n_eval}")

    out_path = ROOT / "data" / "clean" / "split_offense_candidates.json"
    with open(out_path, "w") as f:
        json.dump(candidates, f, indent=2)
    print(f"\nSaved {len(candidates)} candidates to {out_path} for manual review")

    counts_path = ROOT / "results" / "split_offense_candidate_counts.json"
    with open(counts_path, "w") as f:
        json.dump({
            "n_combined_rows": len(all_lines),
            "n_train_rows": len(train_lines),
            "n_eval_rows": len(eval_lines),
            "n_skipped_no_messages": n_no_messages,
            "n_candidates": len(candidates),
            "n_continuing_language": n_cont,
            "n_multi_date_question": n_multi,
            "n_both_signals": n_both,
            "n_train_candidates": n_train,
            "n_eval_candidates": n_eval,
            "note": (
                "Candidate mine only. No routing correctness judged. "
                "Signals: continuing-language in user or assistant; "
                "2+ distinct calendar dates in the user question."
            ),
        }, f, indent=2)
    print(f"Wrote counts to {counts_path}")


if __name__ == "__main__":
    main()
