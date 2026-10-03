import json
import pandas as pd
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

statutes = pd.read_json("data/clean/statutes.jsonl", lines=True)
qa = pd.read_json("data/clean/qa_eval_ready.jsonl", lines=True)

corpus_texts = statutes["text"].tolist()
chunk_ids = statutes["chunk_id"].tolist()
tokenized = [t.lower().split() for t in corpus_texts]
bm25 = BM25Okapi(tokenized)

model = SentenceTransformer("all-MiniLM-L6-v2")
corpus_emb = model.encode(corpus_texts, show_progress_bar=True)

def bm25_ranked(query, k=20):
    scores = bm25.get_scores(query.lower().split())
    top_idx = np.argsort(scores)[::-1][:k]
    return [chunk_ids[i] for i in top_idx]

def dense_ranked(query, k=20):
    q_emb = model.encode([query])
    sims = cosine_similarity(q_emb, corpus_emb)[0]
    top_idx = np.argsort(sims)[::-1][:k]
    return [chunk_ids[i] for i in top_idx]

def hybrid_rrf(query, k=5, pool=20, rrf_k=60):
    bm25_list = bm25_ranked(query, pool)
    dense_list = dense_ranked(query, pool)
    scores = {}
    for rank, cid in enumerate(bm25_list):
        scores[cid] = scores.get(cid, 0) + 1.0 / (rrf_k + rank + 1)
    for rank, cid in enumerate(dense_list):
        scores[cid] = scores.get(cid, 0) + 1.0 / (rrf_k + rank + 1)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [cid for cid, _ in ranked[:k]]

def evaluate(search_fn, name, k=5, sample_size=1000, seed=42):
    sample = qa.sample(min(sample_size, len(qa)), random_state=seed)
    precisions, recalls, rr, ndcgs = [], [], [], []
    per_question_type = {}
    for _, row in sample.iterrows():
        gold = row["chunk_id"]
        retrieved = search_fn(row["question"], k=k)
        hit = gold in retrieved
        rank = retrieved.index(gold) + 1 if hit else 0
        precisions.append(1.0 / k if hit else 0.0)
        recalls.append(1.0 if hit else 0.0)
        rr.append(1.0 / rank if rank else 0.0)
        ndcgs.append(1.0 / np.log2(rank + 1) if rank else 0.0)
        qt = row["question_type"]
        per_question_type.setdefault(qt, []).append(hit)
    return {
        "method": name, "k": k, "n": len(sample),
        "precision_at_k": float(np.mean(precisions)),
        "recall_at_k": float(np.mean(recalls)),
        "mrr": float(np.mean(rr)),
        "ndcg_at_k": float(np.mean(ndcgs)),
        "hit_rate_by_question_type": {qt: float(np.mean(h)) for qt, h in per_question_type.items()},
    }

hybrid_results = evaluate(hybrid_rrf, "Hybrid (RRF, BM25+Dense)")

with open("results/retrieval_eval.json") as f:
    existing = json.load(f)
existing["hybrid"] = hybrid_results
with open("results/retrieval_eval.json", "w") as f:
    json.dump(existing, f, indent=2)

print(json.dumps(hybrid_results, indent=2))
