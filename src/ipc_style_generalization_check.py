"""Paired combined-e5 vs original-e8 on clean (non-leaked) IPC e2e questions."""
import json

import pandas as pd

with open("data/clean/e2e_test_cases.json") as f:
    e2e_cases = json.load(f)

govintel_train = pd.read_json("data/clean/govintel_extracted_v2.jsonl", lines=True)
train_questions = set(govintel_train["question"])

with open("results/end_to_end_pipeline_combined_e5.json") as f:
    combined_full = json.load(f)["results"]
with open("results/end_to_end_pipeline_eval_v2.json") as f:
    e8_full = json.load(f)["results"]

combined_by_q = {r["question"]: r for r in combined_full}
e8_by_q = {r["question"]: r for r in e8_full}

# Clean IPC questions only (confirmed not in combined-e5's exact training set)
clean_ipc_questions = [
    c["question"] for c in e2e_cases
    if c["true_route"] == "IPC" and c["question"] not in train_questions
]

print(f"Clean IPC questions for this check: {len(clean_ipc_questions)}")

n = 0
combined_correct = 0
e8_correct = 0
disagreements = []
for q in clean_ipc_questions:
    if q not in combined_by_q or q not in e8_by_q:
        continue
    n += 1
    c_correct = combined_by_q[q]["end_to_end_correct"]
    e_correct = e8_by_q[q]["end_to_end_correct"]
    combined_correct += int(c_correct)
    e8_correct += int(e_correct)
    if c_correct != e_correct:
        disagreements.append({
            "question": q[:150],
            "gold_chunk_id": combined_by_q[q].get("gold_chunk_id"),
            "combined_e5_correct": bool(c_correct),
            "original_e8_correct": bool(e_correct),
        })

print(f"n = {n}")
print(f"combined-e5: {combined_correct}/{n} = {combined_correct/n:.1%}")
print(f"original-e8: {e8_correct}/{n} = {e8_correct/n:.1%}")
print(f"\nDisagreement cases (one model right, other wrong): {len(disagreements)}")
print(f"  combined-e5 only: {sum(1 for d in disagreements if d['combined_e5_correct'])}")
print(f"  original-e8 only: {sum(1 for d in disagreements if d['original_e8_correct'])}")
for d in disagreements[:15]:
    print(json.dumps(d, indent=2))

with open("results/ipc_style_generalization_check.json", "w") as f:
    json.dump({
        "n": n,
        "combined_e5_acc": combined_correct / n if n else None,
        "e8_acc": e8_correct / n if n else None,
        "n_disagreements": len(disagreements),
        "combined_e5_only_correct": sum(1 for d in disagreements if d["combined_e5_correct"]),
        "e8_only_correct": sum(1 for d in disagreements if d["original_e8_correct"]),
        "disagreements": disagreements,
    }, f, indent=2)
