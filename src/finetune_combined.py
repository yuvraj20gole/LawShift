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

import numpy as np
import pandas as pd
from sentence_transformers import InputExample, SentenceTransformer, losses
from sklearn.metrics.pairwise import cosine_similarity
from torch.utils.data import DataLoader

Path("results").mkdir(parents=True, exist_ok=True)
Path("models").mkdir(parents=True, exist_ok=True)

statutes = pd.read_json("data/clean/statutes.jsonl", lines=True)
statutes_lookup = dict(zip(statutes["chunk_id"], statutes["text"]))
corpus_texts = statutes["text"].tolist()
chunk_ids = statutes["chunk_id"].tolist()
section_numbers = statutes["section_number"].astype(str).str.strip().tolist()

gsms_train = pd.read_json("data/splits/train.jsonl", lines=True)
govintel = pd.read_json("data/clean/govintel_extracted_v2.jsonl", lines=True)
val_df = pd.read_json("data/splits/val.jsonl", lines=True)
test_df = pd.read_json("data/splits/test.jsonl", lines=True)

gsms_pairs = [
    InputExample(texts=[row["question"], statutes_lookup[row["chunk_id"]]])
    for _, row in gsms_train.iterrows() if row["chunk_id"] in statutes_lookup
]
govintel_pairs = [
    InputExample(texts=[row["question"], statutes_lookup[row["chunk_id"]]])
    for _, row in govintel.iterrows() if row["chunk_id"] in statutes_lookup
]

combined = gsms_pairs + govintel_pairs
print(f"GSMS-B pairs: {len(gsms_pairs)}")
print(f"GovIntel pairs: {len(govintel_pairs)}")
print(f"Combined training pairs: {len(combined)}")
print(f"Val: {len(val_df)}, Test: {len(test_df)}")

SECTION_PATTERN = re.compile(
    r"(?:section|sec\.?|§|ipc|bns|bnss|bsa)\s*[:#]?\s*(\d+[A-Za-z]{0,3})",
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
    print(f"Evaluating {model_path} on n={len(eval_df)}...")
    model = SentenceTransformer(model_path)
    corpus_emb = model.encode(corpus_texts, show_progress_bar=True)
    cascade = build_cascade(model, corpus_emb)
    result = evaluate_cascade(cascade, name, eval_df)
    result["model_path"] = model_path
    return result


def fmt(x):
    return f"{x:.4f}"


# ---------------------------------------------------------------------------
# Train combined models
# ---------------------------------------------------------------------------
timing = {}
for n_epochs in [3, 5, 8]:
    out_dir = f"models/finetuned-bge-small-combined-e{n_epochs}"
    marker = Path(out_dir) / "modules.json"
    timing_path = Path(f"results/combined_train_timing_e{n_epochs}.json")
    if marker.exists():
        print(f"Skipping training for combined epochs={n_epochs}; {out_dir} already exists")
        if timing_path.exists():
            with open(timing_path) as f:
                timing[n_epochs] = json.load(f)
        else:
            timing[n_epochs] = {"wall_clock_seconds": None, "note": "reused existing model"}
        continue

    print(f"Training combined dataset for {n_epochs} epochs...")
    model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    train_dataloader = DataLoader(combined, shuffle=True, batch_size=16)
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
        "training_pairs": len(combined),
        "gsms_pairs": len(gsms_pairs),
        "govintel_pairs": len(govintel_pairs),
        "epochs": n_epochs,
    }
    with open(timing_path, "w") as f:
        json.dump(timing[n_epochs], f, indent=2)
    print(f"Saved {out_dir} in {elapsed:.1f}s ({elapsed/60:.1f} min)")

# ---------------------------------------------------------------------------
# Val comparison: original-e8 vs combined-e3/e5/e8
# ---------------------------------------------------------------------------
print("\n=== Validation comparison ===")
configs = {
    "original-e8": {
        "path": "models/finetuned-bge-small-ipc-bns-e8",
        "name": "Original e8 (GSMS-B only)",
        "val_json": Path("results/val_eval_epochs8.json"),
    },
    "combined-e3": {
        "path": "models/finetuned-bge-small-combined-e3",
        "name": "Combined GSMS-B+GovIntel (epochs=3)",
        "val_json": Path("results/combined_val_e3.json"),
    },
    "combined-e5": {
        "path": "models/finetuned-bge-small-combined-e5",
        "name": "Combined GSMS-B+GovIntel (epochs=5)",
        "val_json": Path("results/combined_val_e5.json"),
    },
    "combined-e8": {
        "path": "models/finetuned-bge-small-combined-e8",
        "name": "Combined GSMS-B+GovIntel (epochs=8)",
        "val_json": Path("results/combined_val_e8.json"),
    },
}

val_results = {}
for key, cfg in configs.items():
    if cfg["val_json"].exists():
        with open(cfg["val_json"]) as f:
            val_results[key] = json.load(f)
        print(f"Reusing {cfg['val_json']}")
        continue
    res = evaluate_model_path(cfg["path"], cfg["name"] + " on VAL", val_df)
    with open(cfg["val_json"], "w") as f:
        json.dump(res, f, indent=2)
    val_results[key] = res

with open("results/combined_val_comparison.json", "w") as f:
    json.dump(val_results, f, indent=2)

print("\nVal comparison (k=5):")
print(f"{'config':>14}  {'R@5':>8}  {'MRR':>8}  {'NDCG@5':>8}")
for key in configs:
    r = val_results[key]
    print(f"{key:>14}  {r['recall_at_k']:8.4f}  {r['mrr']:8.4f}  {r['ndcg_at_k']:8.4f}")

winner_key = max(configs.keys(), key=lambda k: val_results[k]["ndcg_at_k"])
print(f"\nWinner by val NDCG@5: {winner_key} ({val_results[winner_key]['ndcg_at_k']:.4f})")

# ---------------------------------------------------------------------------
# Single test eval for winner
# ---------------------------------------------------------------------------
with open("results/final_selected_model_test_eval.json") as f:
    prior_best_test = json.load(f)

if winner_key == "original-e8":
    print("Winner is original-e8 — reusing results/final_selected_model_test_eval.json")
    final_test = dict(prior_best_test)
    final_test["winner_key"] = winner_key
    final_test["note"] = "Reused existing original-e8 test evaluation; no second test run."
else:
    out_test = Path("results/combined_winner_test_eval.json")
    if out_test.exists():
        with open(out_test) as f:
            final_test = json.load(f)
        print("Reusing existing results/combined_winner_test_eval.json")
    else:
        final_test = evaluate_model_path(
            configs[winner_key]["path"],
            configs[winner_key]["name"] + " on TEST",
            test_df,
        )
        final_test["winner_key"] = winner_key
        final_test["note"] = "Single held-out test evaluation of the val-selected combined-data winner."
        with open(out_test, "w") as f:
            json.dump(final_test, f, indent=2)

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def sec_label(n_epochs):
    t = timing.get(n_epochs, {})
    s = t.get("wall_clock_seconds")
    if s is None:
        return t.get("note", "unknown")
    return f"{s:.1f} s ({s/60:.1f} min)"

qt_order = [
    "elements", "exceptions", "definitional_topic",
    "scenario", "definitional_section", "consequence",
]
winner_qt = final_test.get("hit_rate_by_question_type", {})
orig_qt = prior_best_test.get("hit_rate_by_question_type", {})

report = f"""# Combined GSMS-B + GovIntel Fine-tuning — Audit Report

## Objective

Test whether adding {len(govintel_pairs)} GovIntel question–section pairs to the {len(gsms_pairs)} GSMS-B training pairs improves cascade retrieval over the previous best model (`models/finetuned-bge-small-ipc-bns-e8`), using val-then-single-test discipline.

## Method

- **Base model:** `BAAI/bge-small-en-v1.5` (fresh start for combined runs)
- **Training pairs:** {len(gsms_pairs)} GSMS-B (`data/splits/train.jsonl`) + {len(govintel_pairs)} GovIntel (`data/clean/govintel_extracted_v2.jsonl`) = **{len(combined)}**
- **Val / test:** `{len(val_df)}` / `{len(test_df)}` from `data/splits/` (unchanged; GovIntel was contamination-checked against nyaya-eval, not this split)
- **Loss:** `MultipleNegativesRankingLoss`; `[question, gold statute text]`
- **Batch size:** 16; warmup 10% of dataloader length
- **Configs:** combined-e3, combined-e5, combined-e8 vs original-e8 baseline
- **Retrieval:** identical cascade (exact section short-circuit + dense fill), k=5
- **Selection:** highest val NDCG@5; test run once for the winner (reuse original-e8 test file if it wins)

## Environment notes

| Item | Value |
|---|---|
| device | CPU |
| sentence-transformers | 3.4.1 |
| wall-clock combined-e3 | {sec_label(3)} |
| wall-clock combined-e5 | {sec_label(5)} |
| wall-clock combined-e8 | {sec_label(8)} |

## Validation comparison table

Metrics on **`data/splits/val.jsonl` only** (n={len(val_df)}, k=5). Best NDCG@5 in bold.

| Config | Precision@5 | Recall@5 | MRR | NDCG@5 |
|---|---:|---:|---:|---:|
"""

for key in configs:
    r = val_results[key]
    ndcg_cell = f"**{fmt(r['ndcg_at_k'])}**" if key == winner_key else fmt(r["ndcg_at_k"])
    report += (
        f"| {key} | {fmt(r['precision_at_k'])} | {fmt(r['recall_at_k'])} | "
        f"{fmt(r['mrr'])} | {ndcg_cell} |\n"
    )

report += f"""
**Selected winner:** **{winner_key}** (val NDCG@5 = {fmt(val_results[winner_key]['ndcg_at_k'])}).

## Final test result

| Metric | Previous best (original-e8 TEST) | Winner ({winner_key}) TEST |
|---|---:|---:|
| Precision@5 | {fmt(prior_best_test['precision_at_k'])} | {fmt(final_test['precision_at_k'])} |
| Recall@5 | {fmt(prior_best_test['recall_at_k'])} | {fmt(final_test['recall_at_k'])} |
| MRR | {fmt(prior_best_test['mrr'])} | {fmt(final_test['mrr'])} |
| NDCG@5 | {fmt(prior_best_test['ndcg_at_k'])} | {fmt(final_test['ndcg_at_k'])} |

Note: {final_test.get('note', '')}

## Per-question-type breakdown (TEST)

| Question type | original-e8 TEST | Winner ({winner_key}) TEST | Δ |
|---|---:|---:|---:|
"""

for qt in qt_order:
    a = orig_qt.get(qt, float("nan"))
    b = winner_qt.get(qt, float("nan"))
    report += f"| {qt} | {fmt(a)} | {fmt(b)} | {b - a:+.4f} |\n"

ndcgs = [val_results[k]["ndcg_at_k"] for k in ["combined-e3", "combined-e5", "combined-e8"]]
report += f"""
## Observations

- Val NDCG@5: original-e8={fmt(val_results['original-e8']['ndcg_at_k'])}, combined-e3={fmt(val_results['combined-e3']['ndcg_at_k'])}, combined-e5={fmt(val_results['combined-e5']['ndcg_at_k'])}, combined-e8={fmt(val_results['combined-e8']['ndcg_at_k'])}.
- Combined-run val NDCG@5 by epochs 3/5/8: {fmt(ndcgs[0])} / {fmt(ndcgs[1])} / {fmt(ndcgs[2])}.
- Winner by val NDCG@5: **{winner_key}**.
- Test NDCG@5 for the winner: {fmt(final_test['ndcg_at_k'])} (previous best original-e8: {fmt(prior_best_test['ndcg_at_k'])}; Δ {final_test['ndcg_at_k'] - prior_best_test['ndcg_at_k']:+.4f}).
- Test Recall@5 Δ vs original-e8: {final_test['recall_at_k'] - prior_best_test['recall_at_k']:+.4f}; MRR Δ: {final_test['mrr'] - prior_best_test['mrr']:+.4f}.
- Training used {len(combined)} pairs (no hard negatives), batch size 16, MultipleNegativesRankingLoss, CPU.
- Only the val-selected winner received a new test evaluation (or a reuse of original-e8's existing test file).
"""

with open("results/combined_finetuning_report.md", "w") as f:
    f.write(report)

print("\n" + report)
print("Report saved to results/combined_finetuning_report.md")
