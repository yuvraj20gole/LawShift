import json
import re
import pandas as pd
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

statutes = pd.read_json("data/clean/statutes.jsonl", lines=True)
qa = pd.read_json("data/clean/qa_eval_ready.jsonl", lines=True)

corpus_texts = statutes["text"].tolist()
chunk_ids = statutes["chunk_id"].tolist()
section_numbers = statutes["section_number"].astype(str).str.strip().tolist()
tokenized = [t.lower().split() for t in corpus_texts]
bm25 = BM25Okapi(tokenized)

model = SentenceTransformer("all-MiniLM-L6-v2")
corpus_emb = model.encode(corpus_texts, show_progress_bar=True)

def bm25_scores(query):
    return bm25.get_scores(query.lower().split())

def dense_scores(query):
    q_emb = model.encode([query])
    return cosine_similarity(q_emb, corpus_emb)[0]

def minmax(a):
    a = np.array(a, dtype=float)
    if a.max() == a.min():
        return np.zeros_like(a)
    return (a - a.min()) / (a.max() - a.min())

# Strategy A: weighted score fusion, dense weighted much higher than BM25
def weighted_fusion(query, k=5, pool=20, dense_weight=0.85):
    b_scores = bm25_scores(query)
    d_scores = dense_scores(query)
    b_top = set(np.argsort(b_scores)[::-1][:pool].tolist())
    d_top = set(np.argsort(d_scores)[::-1][:pool].tolist())
    candidates = list(b_top | d_top)
    b_norm = minmax([b_scores[i] for i in candidates])
    d_norm = minmax([d_scores[i] for i in candidates])
    combined = dense_weight * d_norm + (1 - dense_weight) * b_norm
    order = np.argsort(combined)[::-1][:k]
    return [chunk_ids[candidates[i]] for i in order]

# Strategy B: cascade — exact section-number short-circuit, dense otherwise
SECTION_PATTERN = re.compile(r'(?:section|sec\.?|§|ipc|bns|bnss|bsa)\s*[:#]?\s*(\d+[a-zA-Z]{0,3})', re.IGNORECASE)

def cascade_search(query, k=5):
    results = []
    triggered = False
    m = SECTION_PATTERN.search(query)
    if m:
        triggered = True
        num = m.group(1)
        exact = [chunk_ids[i] for i, sn in enumerate(section_numbers) if sn == num]
        results.extend(exact)
    d_scores = dense_scores(query)
    d_top = np.argsort(d_scores)[::-1]
    for i in d_top:
        cid = chunk_ids[i]
        if cid not in results:
            results.append(cid)
        if len(results) >= k:
            break
    return results[:k], triggered

def evaluate(search_fn, name, k=5, sample_size=1000, seed=42, tracks_trigger=False):
    sample = qa.sample(min(sample_size, len(qa)), random_state=seed)
    precisions, recalls, rr, ndcgs = [], [], [], []
    per_question_type = {}
    n_triggered = 0
    for _, row in sample.iterrows():
        gold = row["chunk_id"]
        if tracks_trigger:
            retrieved, triggered = search_fn(row["question"], k=k)
            if triggered:
                n_triggered += 1
        else:
            retrieved = search_fn(row["question"], k=k)
        hit = gold in retrieved
        rank = retrieved.index(gold) + 1 if hit else 0
        precisions.append(1.0 / k if hit else 0.0)
        recalls.append(1.0 if hit else 0.0)
        rr.append(1.0 / rank if rank else 0.0)
        ndcgs.append(1.0 / np.log2(rank + 1) if rank else 0.0)
        qt = row["question_type"]
        per_question_type.setdefault(qt, []).append(hit)
    result = {
        "method": name, "k": k, "n": len(sample),
        "precision_at_k": float(np.mean(precisions)),
        "recall_at_k": float(np.mean(recalls)),
        "mrr": float(np.mean(rr)),
        "ndcg_at_k": float(np.mean(ndcgs)),
        "hit_rate_by_question_type": {qt: float(np.mean(h)) for qt, h in per_question_type.items()},
    }
    if tracks_trigger:
        result["section_pattern_trigger_rate"] = n_triggered / len(sample)
    return result

weighted_results = evaluate(weighted_fusion, "Weighted Fusion (0.85 dense / 0.15 BM25)")
cascade_results = evaluate(cascade_search, "Cascade (exact section short-circuit + dense)", tracks_trigger=True)

with open("results/retrieval_eval.json") as f:
    existing = json.load(f)
existing["weighted_fusion"] = weighted_results
existing["cascade"] = cascade_results
with open("results/retrieval_eval.json", "w") as f:
    json.dump(existing, f, indent=2)

print(json.dumps(weighted_results, indent=2))
print(json.dumps(cascade_results, indent=2))
