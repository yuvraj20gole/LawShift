import json
import os
import re
import time
from pathlib import Path

# Prefer PyTorch-only Transformers path; avoid accidental TF import on this host
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, InputExample, losses
from sklearn.metrics.pairwise import cosine_similarity
from torch.utils.data import DataLoader

Path("data/splits").mkdir(parents=True, exist_ok=True)
Path("results").mkdir(parents=True, exist_ok=True)
Path("models").mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Step 1 — train / val / test split (create once; reuse if present)
# ---------------------------------------------------------------------------
split_files = [
    Path("data/splits/train.jsonl"),
    Path("data/splits/val.jsonl"),
    Path("data/splits/test.jsonl"),
]
if all(p.exists() for p in split_files):
    train_df = pd.read_json("data/splits/train.jsonl", lines=True)
    val_df = pd.read_json("data/splits/val.jsonl", lines=True)
    test_df = pd.read_json("data/splits/test.jsonl", lines=True)
    print(f"Reusing saved splits — Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
else:
    qa = pd.read_json("data/clean/qa_eval_ready.jsonl", lines=True)
    qa = qa.sample(frac=1.0, random_state=42).reset_index(drop=True)

    n = len(qa)
    train_end = int(n * 0.8)
    val_end = int(n * 0.9)

    train_df = qa.iloc[:train_end]
    val_df = qa.iloc[train_end:val_end]
    test_df = qa.iloc[val_end:]

    train_df.to_json("data/splits/train.jsonl", orient="records", lines=True)
    val_df.to_json("data/splits/val.jsonl", orient="records", lines=True)
    test_df.to_json("data/splits/test.jsonl", orient="records", lines=True)

    print(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

# ---------------------------------------------------------------------------
# Shared retrieval helpers
# ---------------------------------------------------------------------------
statutes = pd.read_json("data/clean/statutes.jsonl", lines=True)
corpus_texts = statutes["text"].tolist()
chunk_ids = statutes["chunk_id"].tolist()
section_numbers = statutes["section_number"].astype(str).str.strip().tolist()
statutes_lookup = dict(zip(statutes["chunk_id"], statutes["text"]))

SECTION_PATTERN = re.compile(
    r"(?:section|sec\.?|§|ipc|bns|bnss|bsa)\s*[:#]?\s*(\d+[a-zA-Z]{0,3})",
    re.IGNORECASE,
)


def build_cascade(model, corpus_emb):
    def cascade_search(query, k=5):
        results = []
        triggered = False
        m = SECTION_PATTERN.search(query)
        if m:
            triggered = True
            num = m.group(1)
            exact = [chunk_ids[i] for i, sn in enumerate(section_numbers) if sn == num]
            results.extend(exact)
        q_emb = model.encode([query])
        sims = cosine_similarity(q_emb, corpus_emb)[0]
        d_top = np.argsort(sims)[::-1]
        for i in d_top:
            cid = chunk_ids[i]
            if cid not in results:
                results.append(cid)
            if len(results) >= k:
                break
        return results[:k], triggered

    return cascade_search


def evaluate_cascade(search_fn, name, eval_df, k=5):
    precisions, recalls, rr, ndcgs = [], [], [], []
    per_question_type = {}
    n_triggered = 0
    for _, row in eval_df.iterrows():
        gold = row["chunk_id"]
        retrieved, triggered = search_fn(row["question"], k=k)
        if triggered:
            n_triggered += 1
        hit = gold in retrieved
        rank = retrieved.index(gold) + 1 if hit else 0
        precisions.append(1.0 / k if hit else 0.0)
        recalls.append(1.0 if hit else 0.0)
        rr.append(1.0 / rank if rank else 0.0)
        ndcgs.append(1.0 / np.log2(rank + 1) if rank else 0.0)
        qt = row["question_type"]
        per_question_type.setdefault(qt, []).append(hit)
    return {
        "method": name,
        "k": k,
        "n": len(eval_df),
        "precision_at_k": float(np.mean(precisions)),
        "recall_at_k": float(np.mean(recalls)),
        "mrr": float(np.mean(rr)),
        "ndcg_at_k": float(np.mean(ndcgs)),
        "section_pattern_trigger_rate": n_triggered / len(eval_df) if len(eval_df) else None,
        "hit_rate_by_question_type": {
            qt: float(np.mean(h)) for qt, h in per_question_type.items()
        },
    }


# ---------------------------------------------------------------------------
# Step 2 — baseline: cascade + off-the-shelf bge-small on test split
# ---------------------------------------------------------------------------
print("\n=== Step 2: Baseline cascade + BAAI/bge-small-en-v1.5 on test split ===")
baseline_path = Path("results/baseline_on_test_split.json")
if baseline_path.exists():
    with open(baseline_path) as f:
        baseline_results = json.load(f)
    print("Reusing existing baseline results:")
    print(json.dumps(baseline_results, indent=2))
else:
    baseline_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    print("Encoding corpus with baseline bge-small...")
    baseline_corpus_emb = baseline_model.encode(corpus_texts, show_progress_bar=True)
    baseline_cascade = build_cascade(baseline_model, baseline_corpus_emb)
    baseline_results = evaluate_cascade(
        baseline_cascade,
        "Cascade + bge-small-en-v1.5 (before fine-tuning)",
        test_df,
    )
    with open(baseline_path, "w") as f:
        json.dump(baseline_results, f, indent=2)
    print(json.dumps(baseline_results, indent=2))

# ---------------------------------------------------------------------------
# Step 3 — fine-tune on training split
# ---------------------------------------------------------------------------
print("\n=== Step 3: Fine-tuning BAAI/bge-small-en-v1.5 ===")
train_examples = [
    InputExample(texts=[row["question"], statutes_lookup[row["chunk_id"]]])
    for _, row in train_df.iterrows()
    if row["chunk_id"] in statutes_lookup
]
print(f"Training pairs: {len(train_examples)}")

ft_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.MultipleNegativesRankingLoss(ft_model)
warmup_steps = int(len(train_dataloader) * 0.1)
epochs = 3

ft_start = time.time()
ft_model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=epochs,
    warmup_steps=warmup_steps,
    show_progress_bar=True,
    output_path="models/finetuned-bge-small-ipc-bns",
)
ft_elapsed_sec = time.time() - ft_start
print(f"Fine-tuned model saved to models/finetuned-bge-small-ipc-bns")
print(f"Fine-tuning wall-clock time: {ft_elapsed_sec:.1f} seconds ({ft_elapsed_sec/60:.1f} min)")

# ---------------------------------------------------------------------------
# Step 4 — evaluate fine-tuned model on test split
# ---------------------------------------------------------------------------
print("\n=== Step 4: Evaluate fine-tuned model on test split ===")
finetuned_model = SentenceTransformer("models/finetuned-bge-small-ipc-bns")
print("Encoding corpus with fine-tuned bge-small...")
finetuned_corpus_emb = finetuned_model.encode(corpus_texts, show_progress_bar=True)
finetuned_cascade = build_cascade(finetuned_model, finetuned_corpus_emb)
finetuned_results = evaluate_cascade(
    finetuned_cascade,
    "Cascade + bge-small-en-v1.5 (after fine-tuning)",
    test_df,
)
with open("results/finetuned_on_test_split.json", "w") as f:
    json.dump(finetuned_results, f, indent=2)
print(json.dumps(finetuned_results, indent=2))

# ---------------------------------------------------------------------------
# Step 5 — audit report + chart
# ---------------------------------------------------------------------------
print("\n=== Step 5: Writing audit report and chart ===")

# Original Cascade+MiniLM was on a different (non-held-out) sample — load for context only
with open("results/retrieval_eval.json") as f:
    prior = json.load(f)
minilm_cascade = prior["cascade"]

# Chart: before vs after on the held-out test split
metrics = ["Precision@5", "Recall@5", "MRR", "NDCG@5"]
before_vals = [
    baseline_results["precision_at_k"],
    baseline_results["recall_at_k"],
    baseline_results["mrr"],
    baseline_results["ndcg_at_k"],
]
after_vals = [
    finetuned_results["precision_at_k"],
    finetuned_results["recall_at_k"],
    finetuned_results["mrr"],
    finetuned_results["ndcg_at_k"],
]

x = np.arange(len(metrics))
width = 0.35
fig, ax = plt.subplots(figsize=(9, 5))
bars1 = ax.bar(x - width / 2, before_vals, width, label="Before fine-tuning", color="#4C78A8")
bars2 = ax.bar(x + width / 2, after_vals, width, label="After fine-tuning", color="#F58518")
ax.set_ylabel("Score")
ax.set_title("Cascade + bge-small-en-v1.5 — Before vs After Fine-tuning\n(held-out test split, n={})".format(len(test_df)))
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.set_ylim(0, 1.05)
ax.legend()
ax.grid(axis="y", alpha=0.3)
for bars in (bars1, bars2):
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.3f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)
fig.tight_layout()
fig.savefig("results/finetuning_comparison.png", dpi=150)
plt.close(fig)
print("Chart saved to results/finetuning_comparison.png")

# Per-type table helpers
qt_order = [
    "elements",
    "exceptions",
    "definitional_topic",
    "scenario",
    "definitional_section",
    "consequence",
]
before_qt = baseline_results["hit_rate_by_question_type"]
after_qt = finetuned_results["hit_rate_by_question_type"]
minilm_qt = minilm_cascade["hit_rate_by_question_type"]

def fmt(x):
    return f"{x:.4f}"

report = f"""# Fine-tuning Audit Report

## Objective

Measure whether contrastive fine-tuning of `BAAI/bge-small-en-v1.5` on IPC/BNS QA–statute pairs improves cascade retrieval (exact section short-circuit + dense) on a held-out test split that was never used during training.

## Method

- **Corpus:** `data/clean/statutes.jsonl` (1,059 sections from BNS / BNSS / BSA 2023).
- **QA split (seed 42, shuffled once, saved to disk):**
  - Train: `{len(train_df)}` rows → `data/splits/train.jsonl`
  - Val: `{len(val_df)}` rows → `data/splits/val.jsonl` (held out; not used in this run)
  - Test: `{len(test_df)}` rows → `data/splits/test.jsonl`
- **Base embedding model:** `BAAI/bge-small-en-v1.5`
- **Fine-tuning:**
  - Loss: `MultipleNegativesRankingLoss` (in-batch negatives)
  - Training pairs: question ↔ gold statute text for each train row (`{len(train_examples)}` pairs)
  - Epochs: `{epochs}`
  - Batch size: `16`
  - Warmup steps: `{warmup_steps}` (10% of steps per epoch × dataloader length)
  - Output: `models/finetuned-bge-small-ipc-bns`
- **Retrieval protocol (before and after):** identical cascade from `src/final_retrieval_test.py` — if the query matches a section-number regex, promote exact `section_number` matches; fill remaining top-k slots from dense cosine ranking. Evaluated at **k = 5** on **`data/splits/test.jsonl` only**.
- **Context row:** Cascade + MiniLM numbers are from the earlier experiment on a random n=1000 sample of the full QA set (seed 42), not the held-out test split — included for context only, not a fair comparison.

## Environment notes

| Item | Value |
|---|---|
| OS | macOS 26.6.1 (x86_64) |
| Python | 3.11.13 |
| pandas | 2.1.4 |
| numpy | 1.26.4 |
| scikit-learn | 1.8.0 |
| torch | 2.2.2 |
| sentence-transformers | 3.4.1 |
| transformers | 4.46.3 |
| base model | BAAI/bge-small-en-v1.5 |
| fine-tuned model path | models/finetuned-bge-small-ipc-bns |
| fine-tuning wall-clock | {ft_elapsed_sec:.1f} s ({ft_elapsed_sec/60:.1f} min) |

Workarounds that affect reproducibility:

- `sentence-transformers` pinned to **3.4.1** because newer releases require PyTorch ≥ 2.5 (this machine has 2.2.2).
- Dense encoding / training runs used `TRANSFORMERS_NO_TF=1`, `TRANSFORMERS_NO_FLAX=1`, `USE_TF=0`, and `TOKENIZERS_PARALLELISM=false` to avoid a TensorFlow AVX abort on this CPU.
- Training and encoding ran on CPU only (no CUDA).

## Results table

| Method | Eval set | Precision@5 | Recall@5 | MRR | NDCG@5 | Trigger rate |
|---|---|---:|---:|---:|---:|---:|
| Cascade + MiniLM (original, context only) | random n=1000 of full QA | {fmt(minilm_cascade['precision_at_k'])} | {fmt(minilm_cascade['recall_at_k'])} | {fmt(minilm_cascade['mrr'])} | {fmt(minilm_cascade['ndcg_at_k'])} | {fmt(minilm_cascade.get('section_pattern_trigger_rate', float('nan')))} |
| Cascade + bge-small (before fine-tuning) | held-out test split (n={len(test_df)}) | {fmt(baseline_results['precision_at_k'])} | {fmt(baseline_results['recall_at_k'])} | {fmt(baseline_results['mrr'])} | {fmt(baseline_results['ndcg_at_k'])} | {fmt(baseline_results['section_pattern_trigger_rate'])} |
| Cascade + bge-small (after fine-tuning) | held-out test split (n={len(test_df)}) | {fmt(finetuned_results['precision_at_k'])} | {fmt(finetuned_results['recall_at_k'])} | {fmt(finetuned_results['mrr'])} | {fmt(finetuned_results['ndcg_at_k'])} | {fmt(finetuned_results['section_pattern_trigger_rate'])} |

**Note:** Row 1 used a different evaluation sample (non-held-out random draw from the full QA set). Rows 2 and 3 are the only apples-to-apples comparison: same cascade protocol, same `data/splits/test.jsonl`.

Chart: `results/finetuning_comparison.png` (Before vs After on the held-out test split).

## Per-question-type breakdown table

Hit rate at k=5 on the held-out test split, before vs after fine-tuning.

| Question type | Before (bge-small) | After (fine-tuned) | Δ (after − before) |
|---|---:|---:|---:|
"""

for qt in qt_order:
    b = before_qt.get(qt, float("nan"))
    a = after_qt.get(qt, float("nan"))
    report += f"| {qt} | {fmt(b)} | {fmt(a)} | {a - b:+.4f} |\n"

report += f"""
For context only — Cascade + MiniLM hit rates on the earlier n=1000 full-QA sample (not the held-out test split):

| Question type | Cascade + MiniLM (context) |
|---|---:|
"""

for qt in qt_order:
    report += f"| {qt} | {fmt(minilm_qt.get(qt, float('nan')))} |\n"

delta_recall = finetuned_results["recall_at_k"] - baseline_results["recall_at_k"]
delta_mrr = finetuned_results["mrr"] - baseline_results["mrr"]
delta_ndcg = finetuned_results["ndcg_at_k"] - baseline_results["ndcg_at_k"]
delta_p = finetuned_results["precision_at_k"] - baseline_results["precision_at_k"]

best_qt = max(qt_order, key=lambda q: after_qt.get(q, 0) - before_qt.get(q, 0))
worst_qt = min(qt_order, key=lambda q: after_qt.get(q, 0) - before_qt.get(q, 0))

report += f"""
## Observations

- On the held-out test split, fine-tuning changes aggregate metrics by: Precision@5 {delta_p:+.4f}, Recall@5 {delta_recall:+.4f}, MRR {delta_mrr:+.4f}, NDCG@5 {delta_ndcg:+.4f}.
- Before fine-tuning (Cascade + off-the-shelf bge-small) on the test split: Recall@5 {fmt(baseline_results['recall_at_k'])}, MRR {fmt(baseline_results['mrr'])}, NDCG@5 {fmt(baseline_results['ndcg_at_k'])}.
- After fine-tuning (Cascade + fine-tuned bge-small) on the same test split: Recall@5 {fmt(finetuned_results['recall_at_k'])}, MRR {fmt(finetuned_results['mrr'])}, NDCG@5 {fmt(finetuned_results['ndcg_at_k'])}.
- Section-pattern trigger rate on the test split: before {fmt(baseline_results['section_pattern_trigger_rate'])}, after {fmt(finetuned_results['section_pattern_trigger_rate'])} (same cascade regex; rates should be essentially identical).
- Largest per-type hit-rate change (after − before): **{best_qt}** ({after_qt.get(best_qt, 0) - before_qt.get(best_qt, 0):+.4f}).
- Smallest (most negative / least positive) per-type hit-rate change: **{worst_qt}** ({after_qt.get(worst_qt, 0) - before_qt.get(worst_qt, 0):+.4f}).
- Cascade + MiniLM on the earlier non-held-out sample had Recall@5 {fmt(minilm_cascade['recall_at_k'])}; that figure is not directly comparable to the bge-small test-split numbers above.
- Training used {len(train_examples)} question–statute pairs, {epochs} epochs, batch size 16, MultipleNegativesRankingLoss, wall-clock {ft_elapsed_sec/60:.1f} minutes on CPU.
- Precision@5 equals Recall@5 / 5 for each cascade run, which follows from a single gold document per query.
"""

with open("results/finetuning_audit_report.md", "w") as f:
    f.write(report)

print("\n" + report)
print("Report saved to results/finetuning_audit_report.md")

# Persist timing for reference
meta = {
    "train_size": len(train_df),
    "val_size": len(val_df),
    "test_size": len(test_df),
    "training_pairs": len(train_examples),
    "epochs": epochs,
    "batch_size": 16,
    "warmup_steps": warmup_steps,
    "finetuning_wall_clock_seconds": ft_elapsed_sec,
}
with open("results/finetuning_run_meta.json", "w") as f:
    json.dump(meta, f, indent=2)
