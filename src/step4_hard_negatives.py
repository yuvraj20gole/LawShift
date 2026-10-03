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
Path("data/clean").mkdir(parents=True, exist_ok=True)

statutes = pd.read_json("data/clean/statutes.jsonl", lines=True)
train_df = pd.read_json("data/splits/train.jsonl", lines=True)
val_df = pd.read_json("data/splits/val.jsonl", lines=True)
test_df = pd.read_json("data/splits/test.jsonl", lines=True)

statutes_lookup = dict(zip(statutes["chunk_id"], statutes["text"]))
chapter_lookup = dict(zip(statutes["chunk_id"], statutes["chapter"]))
act_lookup = dict(zip(statutes["chunk_id"], statutes["act"]))
corpus_texts = statutes["text"].tolist()
chunk_ids = statutes["chunk_id"].tolist()
section_numbers = statutes["section_number"].astype(str).str.strip().tolist()

print(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

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
# Step 1 — mine hard negatives
# ---------------------------------------------------------------------------
print("\n=== Step 1: Mine hard negatives ===")
hardneg_path = Path("data/clean/hard_negatives.json")
mining_stats_path = Path("results/step4_mining_stats.json")

def same_chapter_negatives(gold_chunk_id, n=2):
    gold_chapter = chapter_lookup.get(gold_chunk_id)
    gold_act = act_lookup.get(gold_chunk_id)
    candidates = statutes[
        (statutes["chapter"] == gold_chapter) &
        (statutes["act"] == gold_act) &
        (statutes["chunk_id"] != gold_chunk_id)
    ]["chunk_id"].tolist()
    return candidates[:n] if candidates else []

if hardneg_path.exists() and mining_stats_path.exists():
    with open(hardneg_path) as f:
        mined = json.load(f)
    with open(mining_stats_path) as f:
        mining_stats = json.load(f)
    print(f"Reusing existing {hardneg_path} ({len(mined)} examples)")
else:
    print("Loading current best model for self-mining...")
    mine_model = SentenceTransformer("models/finetuned-bge-small-ipc-bns-e8")
    print("Encoding corpus for hard-negative mining...")
    mine_corpus_emb = mine_model.encode(texts := corpus_texts, show_progress_bar=True)

    def embedding_negatives(question, gold_chunk_id, n=2, top_k=10):
        q_emb = mine_model.encode([question])
        sims = cosine_similarity(q_emb, mine_corpus_emb)[0]
        order = np.argsort(sims)[::-1][:top_k]
        negs = [chunk_ids[i] for i in order if chunk_ids[i] != gold_chunk_id]
        return negs[:n]

    print("Mining hard negatives for all training examples...")
    mined = []
    n_chapter = []
    n_embed = []
    n_combined = []
    for idx, row in train_df.iterrows():
        gold = row["chunk_id"]
        chapter_negs = same_chapter_negatives(gold, n=2)
        embed_negs = embedding_negatives(row["question"], gold, n=2)
        combined = list(dict.fromkeys(chapter_negs + embed_negs))
        capped = combined[:3]
        mined.append({
            "question": row["question"],
            "gold_chunk_id": gold,
            "hard_negatives": capped,
            "n_same_chapter": len(chapter_negs),
            "n_embedding": len(embed_negs),
        })
        n_chapter.append(len(chapter_negs))
        n_embed.append(len(embed_negs))
        n_combined.append(len(capped))
        if idx % 500 == 0:
            print(f"  {idx}/{len(train_df)}")

    mining_stats = {
        "n_examples": len(mined),
        "n_with_at_least_one_hard_negative": sum(1 for m in mined if m["hard_negatives"]),
        "avg_same_chapter_negatives": float(np.mean(n_chapter)),
        "avg_embedding_negatives": float(np.mean(n_embed)),
        "avg_combined_capped": float(np.mean(n_combined)),
        "same_chapter_requested": 2,
        "embedding_requested": 2,
        "combined_cap": 3,
    }
    with open(hardneg_path, "w") as f:
        json.dump(mined, f, indent=2)
    with open(mining_stats_path, "w") as f:
        json.dump(mining_stats, f, indent=2)

n_with_negs = sum(1 for m in mined if m["hard_negatives"])
print(f"Training examples with at least one hard negative: {n_with_negs} / {len(mined)}")
print(json.dumps(mining_stats, indent=2))

# ---------------------------------------------------------------------------
# Step 2 — fine-tune with explicit hard negatives
# ---------------------------------------------------------------------------
print("\n=== Step 2: Fine-tune with hard negatives ===")
train_examples = []
for m in mined:
    gold_text = statutes_lookup.get(m["gold_chunk_id"])
    if not gold_text:
        continue
    neg_texts = [statutes_lookup[n] for n in m["hard_negatives"] if n in statutes_lookup]
    texts_tuple = [m["question"], gold_text] + neg_texts
    train_examples.append(InputExample(texts=texts_tuple))

print(f"Training pairs with hard negatives: {len(train_examples)}")

timing = {}
for n_epochs in [3, 8]:
    out_dir = f"models/finetuned-bge-small-hardneg-e{n_epochs}"
    marker = Path(out_dir) / "modules.json"
    timing_path = Path(f"results/step4_train_timing_hardneg_e{n_epochs}.json")
    if marker.exists():
        print(f"Skipping training for hardneg epochs={n_epochs}; {out_dir} already exists")
        if timing_path.exists():
            with open(timing_path) as f:
                timing[n_epochs] = json.load(f)
        else:
            timing[n_epochs] = {"wall_clock_seconds": None, "note": "reused existing model; timing unknown"}
        continue

    print(f"Training for {n_epochs} epochs with hard negatives...")
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
        "epochs": n_epochs,
    }
    with open(timing_path, "w") as f:
        json.dump(timing[n_epochs], f, indent=2)
    print(f"Saved {out_dir} in {elapsed:.1f}s ({elapsed/60:.1f} min)")

# ---------------------------------------------------------------------------
# Step 3 — val eval: original-e8, hardneg-e3, hardneg-e8
# ---------------------------------------------------------------------------
print("\n=== Step 3: Validation comparison ===")
configs = {
    "original-e8": {
        "path": "models/finetuned-bge-small-ipc-bns-e8",
        "name": "Original e8 (no hard negatives)",
        "val_json": Path("results/val_eval_epochs8.json"),
        "reuse_existing_val": True,
    },
    "hardneg-e3": {
        "path": "models/finetuned-bge-small-hardneg-e3",
        "name": "Hard-negative fine-tune (epochs=3)",
        "val_json": Path("results/step4_val_hardneg_e3.json"),
        "reuse_existing_val": False,
    },
    "hardneg-e8": {
        "path": "models/finetuned-bge-small-hardneg-e8",
        "name": "Hard-negative fine-tune (epochs=8)",
        "val_json": Path("results/step4_val_hardneg_e8.json"),
        "reuse_existing_val": False,
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
    print(json.dumps({k: res[k] for k in ["method", "recall_at_k", "mrr", "ndcg_at_k"]}, indent=2))

# Keep original-e8 numbers aligned with the prior val file if we reused it
if "recall_at_k" not in val_results["original-e8"] and "val_eval" in str(configs["original-e8"]["val_json"]):
    pass

comparison = {k: val_results[k] for k in configs}
with open("results/step4_val_comparison.json", "w") as f:
    json.dump(comparison, f, indent=2)

print("\nVal comparison (k=5):")
print(f"{'config':>14}  {'R@5':>8}  {'MRR':>8}  {'NDCG@5':>8}")
for key in configs:
    r = val_results[key]
    print(f"{key:>14}  {r['recall_at_k']:8.4f}  {r['mrr']:8.4f}  {r['ndcg_at_k']:8.4f}")

# ---------------------------------------------------------------------------
# Step 4 — select winner, one test eval
# ---------------------------------------------------------------------------
print("\n=== Step 4: Select winner and evaluate test once ===")
winner_key = max(configs.keys(), key=lambda k: val_results[k]["ndcg_at_k"])
print(f"Winner by val NDCG@5: {winner_key} ({val_results[winner_key]['ndcg_at_k']:.4f})")

with open("results/final_selected_model_test_eval.json") as f:
    prior_best_test = json.load(f)

if winner_key == "original-e8":
    print("Winner is original-e8 — reusing results/final_selected_model_test_eval.json")
    final_test = dict(prior_best_test)
    final_test["winner_key"] = winner_key
    final_test["note"] = "Reused existing original-e8 test evaluation; no second test run."
else:
    out_test = Path("results/step4_hardneg_winner_test_eval.json")
    if out_test.exists():
        with open(out_test) as f:
            final_test = json.load(f)
        print("Reusing existing results/step4_hardneg_winner_test_eval.json")
    else:
        final_test = evaluate_model_path(
            configs[winner_key]["path"],
            configs[winner_key]["name"] + " on TEST",
            test_df,
        )
        final_test["winner_key"] = winner_key
        final_test["note"] = "Single held-out test evaluation of the val-selected hard-negative winner."
        with open(out_test, "w") as f:
            json.dump(final_test, f, indent=2)

with open("results/step4_final_test.json", "w") as f:
    json.dump(final_test, f, indent=2)

# ---------------------------------------------------------------------------
# Step 5 — report
# ---------------------------------------------------------------------------
print("\n=== Step 5: Write audit report ===")

def sec_label(n_epochs):
    t = timing.get(n_epochs, {})
    s = t.get("wall_clock_seconds")
    if s is None:
        return t.get("note", "unknown")
    return f"{s:.1f} s ({s/60:.1f} min)"

qt_order = [
    "elements",
    "exceptions",
    "definitional_topic",
    "scenario",
    "definitional_section",
    "consequence",
]
winner_qt = final_test.get("hit_rate_by_question_type", {})
orig_test_qt = prior_best_test.get("hit_rate_by_question_type", {})

report = f"""# Hard-Negative Fine-tuning — Audit Report

## Objective

Test whether adding explicit hard negatives (same-chapter sections plus the current model's own near-misses) improves cascade retrieval over the previous best model (`models/finetuned-bge-small-ipc-bns-e8`), using **val-then-single-test** discipline: compare original-e8, hardneg-e3, and hardneg-e8 on `data/splits/val.jsonl` only; evaluate the winner on `data/splits/test.jsonl` exactly once (reuse the existing original-e8 test file if that config wins).

## Method

- **Base model:** `BAAI/bge-small-en-v1.5` (fresh start for hardneg runs; original-e8 is the prior winner without hard negatives)
- **Train / val / test:** `{len(train_df)}` / `{len(val_df)}` / `{len(test_df)}` from `data/splits/`
- **Loss:** `MultipleNegativesRankingLoss`; each example is `[question, gold_statute, hard_neg, ...]` so extra texts are example-specific in-batch negatives
- **Batch size:** 16; warmup 10% of dataloader length
- **Hard-negative mining (train only):**
  - Same-chapter / same-act: up to 2 neighbors of the gold `chunk_id`
  - Embedding-mined from `models/finetuned-bge-small-ipc-bns-e8`: up to 2 near-misses from the top-10 (excluding gold)
  - Combined, deduped, capped at 3 per example
- **Mining coverage:** {mining_stats.get('n_with_at_least_one_hard_negative', n_with_negs)} / {mining_stats.get('n_examples', len(mined))} examples have ≥1 hard negative
- **Average negatives per example:** same-chapter {mining_stats.get('avg_same_chapter_negatives', float('nan')):.3f}; embedding-mined {mining_stats.get('avg_embedding_negatives', float('nan')):.3f}; after cap {mining_stats.get('avg_combined_capped', float('nan')):.3f}
- **Retrieval protocol:** identical cascade (exact section-number short-circuit + dense fill), k=5
- **Selection:** highest val NDCG@5 among original-e8, hardneg-e3, hardneg-e8

## Environment notes

| Item | Value |
|---|---|
| OS | macOS (x86_64), CPU |
| Python | 3.11 (project `.venv`) |
| torch | 2.2.2 |
| sentence-transformers | 3.4.1 |
| wall-clock hardneg-e3 | {sec_label(3)} |
| wall-clock hardneg-e8 | {sec_label(8)} |

Training used `TRANSFORMERS_NO_TF=1`, `USE_TF=0`, `TORCHDYNAMO_DISABLE=1`.

## Validation comparison table

Metrics on **`data/splits/val.jsonl` only** (n={len(val_df)}, k=5). Best NDCG@5 in bold.

| Config | Precision@5 | Recall@5 | MRR | NDCG@5 |
|---|---:|---:|---:|---:|
"""

for key in ["original-e8", "hardneg-e3", "hardneg-e8"]:
    r = val_results[key]
    ndcg_cell = f"**{fmt(r['ndcg_at_k'])}**" if key == winner_key else fmt(r["ndcg_at_k"])
    report += (
        f"| {key} | {fmt(r['precision_at_k'])} | {fmt(r['recall_at_k'])} | "
        f"{fmt(r['mrr'])} | {ndcg_cell} |\n"
    )

report += f"""
**Selected winner:** **{winner_key}** (val NDCG@5 = {fmt(val_results[winner_key]['ndcg_at_k'])}).

## Final test result

Held-out test for the val-selected winner (`{winner_key}`), vs previous best original-e8 test (Recall@5 0.841, MRR 0.655, NDCG@5 0.702).

| Metric | Previous best (original-e8 TEST) | Winner ({winner_key}) TEST |
|---|---:|---:|
| Precision@5 | {fmt(prior_best_test['precision_at_k'])} | {fmt(final_test['precision_at_k'])} |
| Recall@5 | {fmt(prior_best_test['recall_at_k'])} | {fmt(final_test['recall_at_k'])} |
| MRR | {fmt(prior_best_test['mrr'])} | {fmt(final_test['mrr'])} |
| NDCG@5 | {fmt(prior_best_test['ndcg_at_k'])} | {fmt(final_test['ndcg_at_k'])} |

Note: {final_test.get('note', '')}

## Per-question-type breakdown (TEST)

Hit rate at k=5: original-e8 vs winner. `elements` and `definitional_topic` were the “clearly wrong” categories called out in earlier error analysis.

| Question type | original-e8 TEST | Winner ({winner_key}) TEST | Δ |
|---|---:|---:|---:|
"""

for qt in qt_order:
    a = orig_test_qt.get(qt, float("nan"))
    b = winner_qt.get(qt, float("nan"))
    flag = ""
    if qt in ("elements", "definitional_topic"):
        flag = " ← earlier error-analysis focus"
    report += f"| {qt}{flag} | {fmt(a)} | {fmt(b)} | {b - a:+.4f} |\n"

el_d = winner_qt.get("elements", float("nan")) - orig_test_qt.get("elements", float("nan"))
dt_d = winner_qt.get("definitional_topic", float("nan")) - orig_test_qt.get("definitional_topic", float("nan"))

report += f"""
- `elements` test hit-rate change: {el_d:+.4f}
- `definitional_topic` test hit-rate change: {dt_d:+.4f}

## Observations

- Val NDCG@5: original-e8={fmt(val_results['original-e8']['ndcg_at_k'])}, hardneg-e3={fmt(val_results['hardneg-e3']['ndcg_at_k'])}, hardneg-e8={fmt(val_results['hardneg-e8']['ndcg_at_k'])}.
- Winner by val NDCG@5: **{winner_key}**.
- Test NDCG@5 for the winner: {fmt(final_test['ndcg_at_k'])} (previous best original-e8: {fmt(prior_best_test['ndcg_at_k'])}; Δ {final_test['ndcg_at_k'] - prior_best_test['ndcg_at_k']:+.4f}).
- Test Recall@5 Δ vs original-e8: {final_test['recall_at_k'] - prior_best_test['recall_at_k']:+.4f}; MRR Δ: {final_test['mrr'] - prior_best_test['mrr']:+.4f}.
- Hard-negative training used {len(train_examples)} examples, batch size 16, MultipleNegativesRankingLoss, CPU.
- Only the val-selected winner received a new test evaluation (or a reuse of original-e8's existing test file).
"""

with open("results/step4_hard_negative_report.md", "w") as f:
    f.write(report)

print("\n" + report)
print("Report saved to results/step4_hard_negative_report.md")
