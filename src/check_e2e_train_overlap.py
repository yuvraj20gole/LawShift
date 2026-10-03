"""Check overlap between e2e test cases and combined-e5's GovIntel training pairs."""
import json

import pandas as pd

with open("data/clean/e2e_test_cases.json") as f:
    e2e_cases = json.load(f)
e2e_df = pd.DataFrame(e2e_cases)

govintel_train = pd.read_json("data/clean/govintel_extracted_v2.jsonl", lines=True)

# Exact question-text match first (fastest, catches identical rows)
e2e_questions = set(e2e_df["question"])
train_questions = set(govintel_train["question"])
exact_overlap = e2e_questions & train_questions

print(f"e2e test cases: {len(e2e_df)}")
print(f"combined-e5 training pairs: {len(govintel_train)}")
print(f"EXACT question-text overlap: {len(exact_overlap)} / {len(e2e_df)} ({len(exact_overlap)/len(e2e_df):.1%})")

# Split e2e results by whether they were in combined-e5's training set
with open("results/end_to_end_pipeline_combined_e5.json") as f:
    combined_results = json.load(f)["results"]

clean_results = [r for r in combined_results if r["question"] not in exact_overlap]
leaked_results = [r for r in combined_results if r["question"] in exact_overlap]

print(f"\nClean (NOT in combined-e5 training): {len(clean_results)}")
print(f"Leaked (WAS in combined-e5 training): {len(leaked_results)}")


def acc(results):
    return sum(r["end_to_end_correct"] for r in results) / len(results) if results else None


print(f"\ncombined-e5 accuracy on LEAKED subset: {acc(leaked_results):.1%}" if leaked_results else "No leaked subset")
print(f"combined-e5 accuracy on CLEAN (truly held-out) subset: {acc(clean_results):.1%}" if clean_results else "No clean subset")

clean_ipc = [r for r in clean_results if r["true_route"] == "IPC"]
clean_bns = [r for r in clean_results if r["true_route"] == "BNS"]
print(f"Clean subset IPC (n={len(clean_ipc)}): {acc(clean_ipc):.1%}" if clean_ipc else "")
print(f"Clean subset BNS (n={len(clean_bns)}): {acc(clean_bns):.1%}" if clean_bns else "")

# Also re-check e8 on just the clean subset, for a fair apples-to-apples comparison
with open("results/end_to_end_pipeline_eval_v2.json") as f:
    e8_results = json.load(f)["results"]
e8_by_question = {r["question"]: r for r in e8_results}
e8_clean = [e8_by_question[r["question"]] for r in clean_results if r["question"] in e8_by_question]
print(f"\noriginal-e8 accuracy on the SAME clean subset (n={len(e8_clean)}): {acc(e8_clean):.1%}")

e8_clean_ipc = [r for r in e8_clean if r["true_route"] == "IPC"]
e8_clean_bns = [r for r in e8_clean if r["true_route"] == "BNS"]
print(f"original-e8 clean IPC (n={len(e8_clean_ipc)}): {acc(e8_clean_ipc):.1%}" if e8_clean_ipc else "")
print(f"original-e8 clean BNS (n={len(e8_clean_bns)}): {acc(e8_clean_bns):.1%}" if e8_clean_bns else "")

with open("results/contamination_corrected_comparison.json", "w") as f:
    json.dump({
        "n_total": len(e2e_df),
        "n_exact_overlap": len(exact_overlap),
        "overlap_rate": len(exact_overlap) / len(e2e_df),
        "n_clean": len(clean_results),
        "n_leaked": len(leaked_results),
        "combined_e5_leaked_acc": acc(leaked_results),
        "combined_e5_clean_acc": acc(clean_results),
        "combined_e5_clean_ipc": acc(clean_ipc),
        "combined_e5_clean_bns": acc(clean_bns),
        "e8_clean_acc": acc(e8_clean),
        "e8_clean_ipc": acc(e8_clean_ipc),
        "e8_clean_bns": acc(e8_clean_bns),
    }, f, indent=2)
