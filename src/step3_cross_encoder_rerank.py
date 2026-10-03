import pandas as pd
import numpy as np
import re
import os
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity
import json

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")

statutes = pd.read_json("data/clean/statutes.jsonl", lines=True)
val = pd.read_json("data/splits/val.jsonl", lines=True)

chunk_ids = statutes["chunk_id"].tolist()
section_numbers = statutes["section_number"].astype(str).str.strip().tolist()
texts = statutes["text"].tolist()
text_by_chunk = dict(zip(chunk_ids, texts))

bi_encoder = SentenceTransformer("models/finetuned-bge-small-ipc-bns-e8")
print("Encoding corpus with bi-encoder...")
corpus_emb = bi_encoder.encode(texts, show_progress_bar=True)

print("Loading cross-encoder...")
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

SECTION_PATTERN = re.compile(r'(?:section|sec\.?|§|ipc|bns|bnss|bsa)\s*[:#]?\s*(\d+[a-zA-Z]{0,3})', re.IGNORECASE)

def get_candidate_pool(query, pool_size=30):
    """Same exact-match short-circuit as before, then bi-encoder similarity for the rest."""
    results = []
    m = SECTION_PATTERN.search(query)
    if m:
        num = m.group(1)
        exact = [chunk_ids[i] for i, sn in enumerate(section_numbers) if sn == num]
        results.extend(exact)
    q_emb = bi_encoder.encode([query])
    sims = cosine_similarity(q_emb, corpus_emb)[0]
    order = np.argsort(sims)[::-1]
    for i in order:
        cid = chunk_ids[i]
        if cid not in results:
            results.append(cid)
        if len(results) >= pool_size:
            break
    return results[:pool_size]

def rerank_search(query, k=5, pool_size=30):
    pool = get_candidate_pool(query, pool_size)
    pairs = [[query, text_by_chunk[cid]] for cid in pool]
    scores = cross_encoder.predict(pairs)
    ranked = [cid for _, cid in sorted(zip(scores, pool), key=lambda x: x[0], reverse=True)]
    return ranked[:k]

def baseline_search(query, k=5):
    return get_candidate_pool(query, pool_size=k)

def evaluate(search_fn, name, k=5):
    hits, rr, ndcgs = [], [], []
    per_question_type = {}
    for _, row in val.iterrows():
        gold = row["chunk_id"]
        retrieved = search_fn(row["question"], k=k)
        hit = gold in retrieved
        rank = retrieved.index(gold) + 1 if hit else 0
        hits.append(hit)
        rr.append(1.0 / rank if rank else 0.0)
        ndcgs.append(1.0 / np.log2(rank + 1) if rank else 0.0)
        qt = row["question_type"]
        per_question_type.setdefault(qt, []).append(hit)
    return {
        "method": name, "k": k, "n": len(val),
        "recall_at_k": float(np.mean(hits)),
        "mrr": float(np.mean(rr)),
        "ndcg_at_k": float(np.mean(ndcgs)),
        "hit_rate_by_question_type": {qt: float(np.mean(h)) for qt, h in per_question_type.items()},
    }

print("Evaluating baseline (bi-encoder cascade, no re-ranking)...")
baseline_results = evaluate(baseline_search, "Bi-encoder only (baseline)")

print("Evaluating with cross-encoder re-ranking...")
rerank_results = evaluate(rerank_search, "Bi-encoder retrieve top-30 + Cross-encoder rerank")

results = {"baseline": baseline_results, "reranked": rerank_results}
with open("results/step3_cross_encoder_eval.json", "w") as f:
    json.dump(results, f, indent=2)

report = f"""# Cross-Encoder Re-ranking — Audit Report (Off-the-shelf, No Fine-tuning)

## Objective
Test whether re-ranking the bi-encoder's top-30 candidates with a pretrained
cross-encoder (not fine-tuned on our data) improves retrieval, before investing
time in fine-tuning a cross-encoder on our own training data.

## Method
- Bi-encoder: models/finetuned-bge-small-ipc-bns-e8 (retrieves top-30 candidate pool)
- Cross-encoder: cross-encoder/ms-marco-MiniLM-L-6-v2 (off-the-shelf, general-domain, NOT fine-tuned on IPC/BNS data)
- Eval set: data/splits/val.jsonl (n={len(val)}), test untouched
- k = 5 for final results in both conditions

## Results

| Method | Recall@5 | MRR | NDCG@5 |
|---|---:|---:|---:|
| Bi-encoder only (baseline) | {baseline_results['recall_at_k']:.4f} | {baseline_results['mrr']:.4f} | {baseline_results['ndcg_at_k']:.4f} |
| + Cross-encoder rerank (off-the-shelf) | {rerank_results['recall_at_k']:.4f} | {rerank_results['mrr']:.4f} | {rerank_results['ndcg_at_k']:.4f} |

## Per-question-type breakdown

| Question type | Baseline | Reranked | Delta |
|---|---:|---:|---:|
"""
for qt in baseline_results["hit_rate_by_question_type"]:
    b = baseline_results["hit_rate_by_question_type"][qt]
    r = rerank_results["hit_rate_by_question_type"].get(qt, 0)
    report += f"| {qt} | {b:.4f} | {r:.4f} | {r-b:+.4f} |\n"

report += f"""
## Observations
- Overall Recall@5 change from re-ranking: {rerank_results['recall_at_k'] - baseline_results['recall_at_k']:+.4f}
- Overall NDCG@5 change: {rerank_results['ndcg_at_k'] - baseline_results['ndcg_at_k']:+.4f}
- This cross-encoder has NOT been fine-tuned on legal/IPC/BNS data — it is a general
  passage-relevance model. A positive result here means the approach is worth fine-tuning
  further; a flat or negative result means off-the-shelf domain mismatch is limiting it,
  and fine-tuning the cross-encoder on our training pairs should be tried before abandoning
  this direction.
"""

with open("results/step3_cross_encoder_report.md", "w") as f:
    f.write(report)

print(report)
