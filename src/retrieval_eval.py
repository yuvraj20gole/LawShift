import json
import pandas as pd
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

statutes = pd.read_json("data/clean/statutes.jsonl", lines=True)
qa = pd.read_json("data/clean/qa_eval_ready.jsonl", lines=True)

# --- BM25 index ---
corpus_texts = statutes["text"].tolist()
tokenized = [t.lower().split() for t in corpus_texts]
bm25 = BM25Okapi(tokenized)

def bm25_search(query, k=5):
    scores = bm25.get_scores(query.lower().split())
    top_idx = np.argsort(scores)[::-1][:k]
    return statutes.iloc[top_idx]["chunk_id"].tolist()

# --- Dense baseline ---
print("Encoding corpus with sentence-transformers (this takes a minute)...")
model = SentenceTransformer("all-MiniLM-L6-v2")
corpus_emb = model.encode(corpus_texts, show_progress_bar=True)

def dense_search(query, k=5):
    q_emb = model.encode([query])
    sims = cosine_similarity(q_emb, corpus_emb)[0]
    top_idx = np.argsort(sims)[::-1][:k]
    return statutes.iloc[top_idx]["chunk_id"].tolist()

def evaluate(search_fn, name, k=5, sample_size=1000):
    sample = qa.sample(min(sample_size, len(qa)), random_state=42)
    precisions, recalls, rr, ndcgs = [], [], [], []
    per_question_type = {}

    for _, row in sample.iterrows():
        gold = row["chunk_id"]
        retrieved = search_fn(row["question"], k=k)
        hit = gold in retrieved
        rank = retrieved.index(gold) + 1 if hit else 0

        p = 1.0 / k if hit else 0.0
        r = 1.0 if hit else 0.0
        m = 1.0 / rank if rank else 0.0
        n = 1.0 / np.log2(rank + 1) if rank else 0.0

        precisions.append(p); recalls.append(r); rr.append(m); ndcgs.append(n)

        qt = row["question_type"]
        per_question_type.setdefault(qt, []).append(hit)

    per_type_accuracy = {qt: float(np.mean(hits)) for qt, hits in per_question_type.items()}

    return {
        "method": name, "k": k, "n": len(sample),
        "precision_at_k": float(np.mean(precisions)),
        "recall_at_k": float(np.mean(recalls)),
        "mrr": float(np.mean(rr)),
        "ndcg_at_k": float(np.mean(ndcgs)),
        "hit_rate_by_question_type": per_type_accuracy,
    }

print("Evaluating BM25...")
bm25_results = evaluate(bm25_search, "BM25")
print("Evaluating dense baseline...")
dense_results = evaluate(dense_search, "Dense (MiniLM)")

with open("results/retrieval_eval.json", "w") as f:
    json.dump({"bm25": bm25_results, "dense": dense_results}, f, indent=2)

print(json.dumps(bm25_results, indent=2))
print(json.dumps(dense_results, indent=2))
