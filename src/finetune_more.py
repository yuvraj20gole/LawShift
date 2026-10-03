import json
import os
import re
import time
from pathlib import Path

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

Path("results").mkdir(parents=True, exist_ok=True)
Path("models").mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Shared data + cascade helpers (same protocol as finetune_retrieval.py)
# ---------------------------------------------------------------------------
statutes = pd.read_json("data/clean/statutes.jsonl", lines=True)
corpus_texts = statutes["text"].tolist()
chunk_ids = statutes["chunk_id"].tolist()
section_numbers = statutes["section_number"].astype(str).str.strip().tolist()
statutes_lookup = dict(zip(statutes["chunk_id"], statutes["text"]))

train_df = pd.read_json("data/splits/train.jsonl", lines=True)
val_df = pd.read_json("data/splits/val.jsonl", lines=True)
test_df = pd.read_json("data/splits/test.jsonl", lines=True)

print(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

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


def evaluate_model_path(model_path, name, eval_df):
    print(f"Evaluating {model_path} on {name} set (n={len(eval_df)})...")
    model = SentenceTransformer(model_path)
    corpus_emb = model.encode(corpus_texts, show_progress_bar=True)
    cascade = build_cascade(model, corpus_emb)
    return evaluate_cascade(cascade, name, eval_df)


def fmt(x):
    return f"{x:.4f}"


# ---------------------------------------------------------------------------
# Step 1 — val eval for existing epochs=3 model
# ---------------------------------------------------------------------------
print("\n=== Step 1: Val eval for existing epochs=3 model ===")
e3_path = "models/finetuned-bge-small-ipc-bns"
e3_val_path = Path("results/val_eval_epochs3.json")
if e3_val_path.exists():
    with open(e3_val_path) as f:
        val_e3 = json.load(f)
    print("Reusing existing results/val_eval_epochs3.json")
else:
    val_e3 = evaluate_model_path(
        e3_path,
        "Cascade + fine-tuned bge-small (epochs=3) on VAL",
        val_df,
    )
    val_e3["epochs"] = 3
    val_e3["model_path"] = e3_path
    with open(e3_val_path, "w") as f:
        json.dump(val_e3, f, indent=2)
print(json.dumps(val_e3, indent=2))

# ---------------------------------------------------------------------------
# Step 2 — fine-tune epochs 5, 8, 15
# ---------------------------------------------------------------------------
print("\n=== Step 2: Fine-tune additional epoch configs ===")
train_examples = [
    InputExample(texts=[row["question"], statutes_lookup[row["chunk_id"]]])
    for _, row in train_df.iterrows()
    if row["chunk_id"] in statutes_lookup
]
print(f"Training pairs: {len(train_examples)}")

timing = {}
# epochs=3 already trained; record prior wall-clock if available
prior_meta = Path("results/finetuning_run_meta.json")
if prior_meta.exists():
    with open(prior_meta) as f:
        prior = json.load(f)
    timing[3] = {
        "wall_clock_seconds": prior.get("finetuning_wall_clock_seconds"),
        "note": "from prior fine-tuning run",
    }

for n_epochs in [5, 8, 15]:
    out_dir = f"models/finetuned-bge-small-ipc-bns-e{n_epochs}"
    marker = Path(out_dir) / "modules.json"
    if marker.exists():
        print(f"Skipping training for epochs={n_epochs}; {out_dir} already exists")
        timing_path = Path(f"results/train_timing_epochs{n_epochs}.json")
        if timing_path.exists():
            with open(timing_path) as f:
                timing[n_epochs] = json.load(f)
        else:
            timing[n_epochs] = {"wall_clock_seconds": None, "note": "reused existing model; timing unknown"}
        continue

    print(f"\nTraining for {n_epochs} epochs...")
    model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
    train_loss = losses.MultipleNegativesRankingLoss(model)
    warmup_steps = int(len(train_dataloader) * 0.1)
    t0 = time.time()
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=n_epochs,
        warmup_steps=warmup_steps,
        show_progress_bar=True,
        output_path=out_dir,
    )
    elapsed = time.time() - t0
    timing[n_epochs] = {
        "wall_clock_seconds": elapsed,
        "warmup_steps": warmup_steps,
        "batch_size": 16,
        "training_pairs": len(train_examples),
    }
    with open(f"results/train_timing_epochs{n_epochs}.json", "w") as f:
        json.dump(timing[n_epochs], f, indent=2)
    print(f"Saved {out_dir} in {elapsed:.1f}s ({elapsed/60:.1f} min)")

with open("results/second_finetuning_timings.json", "w") as f:
    json.dump(timing, f, indent=2, default=str)

# ---------------------------------------------------------------------------
# Step 3 — val eval for e5, e8, e15
# ---------------------------------------------------------------------------
print("\n=== Step 3: Val eval for epochs 5, 8, 15 ===")
val_results = {3: val_e3}
model_paths = {
    3: "models/finetuned-bge-small-ipc-bns",
    5: "models/finetuned-bge-small-ipc-bns-e5",
    8: "models/finetuned-bge-small-ipc-bns-e8",
    15: "models/finetuned-bge-small-ipc-bns-e15",
}

for n_epochs in [5, 8, 15]:
    out_json = Path(f"results/val_eval_epochs{n_epochs}.json")
    if out_json.exists():
        with open(out_json) as f:
            val_results[n_epochs] = json.load(f)
        print(f"Reusing {out_json}")
        continue
    res = evaluate_model_path(
        model_paths[n_epochs],
        f"Cascade + fine-tuned bge-small (epochs={n_epochs}) on VAL",
        val_df,
    )
    res["epochs"] = n_epochs
    res["model_path"] = model_paths[n_epochs]
    with open(out_json, "w") as f:
        json.dump(res, f, indent=2)
    val_results[n_epochs] = res
    print(json.dumps(res, indent=2))

# ---------------------------------------------------------------------------
# Step 4 — pick winner by highest val NDCG@5
# ---------------------------------------------------------------------------
print("\n=== Step 4: Validation comparison & winner selection ===")
epoch_order = [3, 5, 8, 15]
print("\nValidation comparison (k=5, val n={}):".format(len(val_df)))
print(f"{'epochs':>8}  {'P@5':>8}  {'R@5':>8}  {'MRR':>8}  {'NDCG@5':>8}")
for e in epoch_order:
    r = val_results[e]
    print(
        f"{e:>8}  {r['precision_at_k']:8.4f}  {r['recall_at_k']:8.4f}  "
        f"{r['mrr']:8.4f}  {r['ndcg_at_k']:8.4f}"
    )

winner_epochs = max(epoch_order, key=lambda e: val_results[e]["ndcg_at_k"])
winner = val_results[winner_epochs]
ndcg_curve = [val_results[e]["ndcg_at_k"] for e in epoch_order]

# Characterize curve shape
peak_epochs = epoch_order[int(np.argmax(ndcg_curve))]
last = ndcg_curve[-1]
peak = max(ndcg_curve)
# still climbing if max is at final epoch and last > previous
if peak_epochs == 15 and ndcg_curve[-1] >= ndcg_curve[-2] - 1e-12:
    if abs(ndcg_curve[-1] - ndcg_curve[-2]) < 0.005:
        curve_shape = "plateaued near epoch 15 (val NDCG@5 still highest or tied at the final config, but gain from 8→15 is < 0.005)"
    else:
        curve_shape = "still climbing at epoch 15 (val NDCG@5 highest at the largest epoch count)"
elif peak_epochs < 15 and last < peak - 1e-12:
    curve_shape = (
        f"dropped after peaking at epoch {peak_epochs} "
        f"(val NDCG@5 at 15 = {last:.4f} < peak {peak:.4f}) — overfitting signal; "
        f"winner is epochs={winner_epochs}, not 15"
    )
else:
    curve_shape = (
        f"plateaued around epoch {peak_epochs} "
        f"(val NDCG@5 no longer clearly improving through epoch 15)"
    )

print(f"\nWinner by highest val NDCG@5: epochs={winner_epochs} (NDCG@5={winner['ndcg_at_k']:.4f})")
print(f"Curve shape: {curve_shape}")

selection = {
    "winner_epochs": winner_epochs,
    "winner_model_path": model_paths[winner_epochs],
    "winner_val_ndcg_at_k": winner["ndcg_at_k"],
    "val_ndcg_by_epochs": {str(e): val_results[e]["ndcg_at_k"] for e in epoch_order},
    "curve_shape": curve_shape,
}
with open("results/second_finetuning_selection.json", "w") as f:
    json.dump(selection, f, indent=2)

# ---------------------------------------------------------------------------
# Step 5 — one final test eval for the winner
# ---------------------------------------------------------------------------
print("\n=== Step 5: Final test evaluation for winning config ===")
with open("results/finetuned_on_test_split.json") as f:
    test_e3 = json.load(f)

if winner_epochs == 3:
    print("Winner is epochs=3 — reusing results/finetuned_on_test_split.json")
    final_test = dict(test_e3)
    final_test["epochs"] = 3
    final_test["model_path"] = model_paths[3]
    final_test["note"] = "Reused existing epochs=3 test evaluation; no second test run."
    with open("results/final_selected_model_test_eval.json", "w") as f:
        json.dump(final_test, f, indent=2)
else:
    out_test = Path("results/final_selected_model_test_eval.json")
    if out_test.exists():
        with open(out_test) as f:
            final_test = json.load(f)
        print("Reusing existing results/final_selected_model_test_eval.json")
    else:
        final_test = evaluate_model_path(
            model_paths[winner_epochs],
            f"Cascade + fine-tuned bge-small (epochs={winner_epochs}) on TEST",
            test_df,
        )
        final_test["epochs"] = winner_epochs
        final_test["model_path"] = model_paths[winner_epochs]
        final_test["note"] = "Single held-out test evaluation of the val-selected winner."
        with open(out_test, "w") as f:
            json.dump(final_test, f, indent=2)
print(json.dumps(final_test, indent=2))

# ---------------------------------------------------------------------------
# Step 6 — chart + audit report
# ---------------------------------------------------------------------------
print("\n=== Step 6: Chart + audit report ===")

# Line chart: val recall / MRR / NDCG vs epochs
fig, ax = plt.subplots(figsize=(9, 5))
xs = epoch_order
recall_vals = [val_results[e]["recall_at_k"] for e in xs]
mrr_vals = [val_results[e]["mrr"] for e in xs]
ndcg_vals = [val_results[e]["ndcg_at_k"] for e in xs]
ax.plot(xs, recall_vals, marker="o", label="Recall@5", color="#4C78A8")
ax.plot(xs, mrr_vals, marker="s", label="MRR", color="#F58518")
ax.plot(xs, ndcg_vals, marker="D", label="NDCG@5", color="#54A24B")
ax.set_xticks(xs)
ax.set_xlabel("Epochs")
ax.set_ylabel("Score (validation)")
ax.set_title(f"Validation metrics vs epochs (n={len(val_df)})\nWinner by NDCG@5: epochs={winner_epochs}")
ax.set_ylim(0, 1.05)
ax.grid(alpha=0.3)
ax.legend()
for x, y in zip(xs, ndcg_vals):
    ax.annotate(f"{y:.3f}", (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8)
fig.tight_layout()
fig.savefig("results/epoch_comparison_val.png", dpi=150)
plt.close(fig)
print("Chart saved to results/epoch_comparison_val.png")

qt_order = [
    "elements",
    "exceptions",
    "definitional_topic",
    "scenario",
    "definitional_section",
    "consequence",
]
winner_qt = final_test.get("hit_rate_by_question_type", {})
e3_qt = test_e3.get("hit_rate_by_question_type", {})

def sec(e):
    t = timing.get(e, {})
    s = t.get("wall_clock_seconds")
    if s is None:
        return "unknown"
    return f"{s:.1f} s ({s/60:.1f} min)"

report = f"""# Second Fine-tuning Audit Report

## Objective

Compare four fine-tuning epoch budgets (3, 5, 8, 15) for `BAAI/bge-small-en-v1.5` under the cascade retrieval protocol, using **proper val-then-single-test discipline**: all four configs are compared on `data/splits/val.jsonl` only; the winner (highest val NDCG@5) is confirmed on `data/splits/test.jsonl` **exactly once**. No config other than the winner is evaluated on the held-out test set in this run (except that epochs=3 already had a prior test number, reused only if it wins).

## Method

- **Corpus:** `data/clean/statutes.jsonl` (1,059 sections).
- **Splits (seed 42, fixed on disk):**
  - Train: `{len(train_df)}` → `data/splits/train.jsonl`
  - Val: `{len(val_df)}` → `data/splits/val.jsonl` (model selection)
  - Test: `{len(test_df)}` → `data/splits/test.jsonl` (final confirmation only)
- **Base model:** `BAAI/bge-small-en-v1.5`
- **Training pairs:** `{len(train_examples)}` question ↔ gold statute text pairs from train
- **Loss:** `MultipleNegativesRankingLoss` (in-batch negatives)
- **Batch size:** 16
- **Warmup:** 10% of dataloader length
- **Configs trained / compared:**
  | Epochs | Model path | Trained in this run? |
  |---|---|---|
  | 3 | `models/finetuned-bge-small-ipc-bns` | No (prior run) |
  | 5 | `models/finetuned-bge-small-ipc-bns-e5` | Yes (unless already present) |
  | 8 | `models/finetuned-bge-small-ipc-bns-e8` | Yes (unless already present) |
  | 15 | `models/finetuned-bge-small-ipc-bns-e15` | Yes (unless already present) |
- **Retrieval protocol:** identical cascade (exact section-number short-circuit + dense fill) at **k = 5**
- **Selection rule:** highest **NDCG@5 on val**; test run only for the winner

## Environment notes

| Item | Value |
|---|---|
| OS | macOS 26.6.1 (x86_64) |
| Python | 3.11.13 (project `.venv`) |
| torch | 2.2.2 |
| sentence-transformers | 3.4.1 |
| transformers | 4.46.3 |
| device | CPU |
| wall-clock epochs=3 | {sec(3)} |
| wall-clock epochs=5 | {sec(5)} |
| wall-clock epochs=8 | {sec(8)} |
| wall-clock epochs=15 | {sec(15)} |

Workarounds: training ran in `.venv` (no TensorFlow) with `TRANSFORMERS_NO_TF=1`, `USE_TF=0`, `TORCHDYNAMO_DISABLE=1` because system TensorFlow 2.16.2 AVX-aborts this CPU.

## Validation comparison table

Metrics on **`data/splits/val.jsonl` only** (n={len(val_df)}, k=5). Best NDCG@5 in bold.

| Epochs | Precision@5 | Recall@5 | MRR | NDCG@5 |
|---|---:|---:|---:|---:|
"""

for e in epoch_order:
    r = val_results[e]
    ndcg_cell = f"**{fmt(r['ndcg_at_k'])}**" if e == winner_epochs else fmt(r["ndcg_at_k"])
    report += (
        f"| {e} | {fmt(r['precision_at_k'])} | {fmt(r['recall_at_k'])} | "
        f"{fmt(r['mrr'])} | {ndcg_cell} |\n"
    )

report += f"""
**Selected winner:** epochs=**{winner_epochs}** (highest val NDCG@5 = {fmt(winner['ndcg_at_k'])}).

**Val curve shape:** {curve_shape}

Chart: `results/epoch_comparison_val.png`

## Final test result

Definitive held-out test numbers for the **val-selected winner** (epochs={winner_epochs}), evaluated on `data/splits/test.jsonl` (n={len(test_df)}, k=5).

| Metric | Winner (epochs={winner_epochs}) on TEST |
|---|---:|
| Precision@5 | {fmt(final_test['precision_at_k'])} |
| Recall@5 | {fmt(final_test['recall_at_k'])} |
| MRR | {fmt(final_test['mrr'])} |
| NDCG@5 | {fmt(final_test['ndcg_at_k'])} |
| Section trigger rate | {fmt(final_test.get('section_pattern_trigger_rate') or float('nan'))} |

Model path: `{final_test.get('model_path', model_paths[winner_epochs])}`

Note: {final_test.get('note', 'Single test evaluation of val winner.')}

Prior epochs=3 test numbers (for comparison; only the winner’s test row above is the selection outcome):

| Metric | epochs=3 on TEST (prior) |
|---|---:|
| Precision@5 | {fmt(test_e3['precision_at_k'])} |
| Recall@5 | {fmt(test_e3['recall_at_k'])} |
| MRR | {fmt(test_e3['mrr'])} |
| NDCG@5 | {fmt(test_e3['ndcg_at_k'])} |

## Per-question-type breakdown

Hit rate at k=5 on the **test** set: winning model vs prior epochs=3 test numbers.

| Question type | epochs=3 (test) | Winner epochs={winner_epochs} (test) | Δ |
|---|---:|---:|---:|
"""

for qt in qt_order:
    a = e3_qt.get(qt, float("nan"))
    b = winner_qt.get(qt, float("nan"))
    report += f"| {qt} | {fmt(a)} | {fmt(b)} | {b - a:+.4f} |\n"

# Observations about climbing / plateau / drop
ndcg3, ndcg5, ndcg8, ndcg15 = ndcg_curve
report += f"""
## Observations

- Val NDCG@5 by epochs: 3={fmt(ndcg3)}, 5={fmt(ndcg5)}, 8={fmt(ndcg8)}, 15={fmt(ndcg15)}.
- Winner selected by highest val NDCG@5: **epochs={winner_epochs}**.
- Curve characterization: **{curve_shape}**
- This answers “should we train more?” under the observed val evidence: the selected epoch count is {winner_epochs}, not automatically the largest budget.
- Final test NDCG@5 for the winner: **{fmt(final_test['ndcg_at_k'])}** (Recall@5 {fmt(final_test['recall_at_k'])}, MRR {fmt(final_test['mrr'])}).
- Relative to the prior epochs=3 test run: Δ NDCG@5 = {final_test['ndcg_at_k'] - test_e3['ndcg_at_k']:+.4f}, Δ Recall@5 = {final_test['recall_at_k'] - test_e3['recall_at_k']:+.4f}, Δ MRR = {final_test['mrr'] - test_e3['mrr']:+.4f}.
- Only the winning config received a new (or reused-if-e3) test evaluation in this selection procedure; e5/e8/e15 were judged on val only.
- Training used {len(train_examples)} pairs, batch size 16, MultipleNegativesRankingLoss, CPU.
"""

with open("results/second_finetuning_audit_report.md", "w") as f:
    f.write(report)

print("\n" + report)
print("Report saved to results/second_finetuning_audit_report.md")
