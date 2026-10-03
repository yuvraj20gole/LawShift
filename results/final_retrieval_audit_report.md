# Final Retrieval Audit Report

## Objective

Compare five statute-section retrieval strategies — BM25, Dense MiniLM, Hybrid RRF, Weighted Score Fusion, and Cascade (exact section short-circuit + dense) — under an identical evaluation protocol, and identify which method recovers the gold `chunk_id` most reliably.

## Method

- **Corpus:** `data/clean/statutes.jsonl` (1,059 sections from BNS / BNSS / BSA 2023).
- **Queries:** `data/clean/qa_eval_ready.jsonl`; a random sample of **n = 1,000** questions, `random_state` / seed **42**.
- **Gold label:** the QA row’s `chunk_id` (exactly one relevant document per query).
- **k:** 5 (Precision@5, Recall@5, MRR, NDCG@5; NDCG uses a binary relevance gain of 1 at the gold rank).
- **BM25:** `rank_bm25.BM25Okapi` on whitespace-tokenized lowercase statute text; top-k by BM25 score. Source: `src/retrieval_eval.py`.
- **Dense:** `sentence-transformers` model `all-MiniLM-L6-v2`; cosine similarity of the question embedding against precomputed corpus embeddings; top-k. Source: `src/retrieval_eval.py`.
- **Hybrid RRF:** BM25 top-20 ∪ Dense top-20 fused with Reciprocal Rank Fusion, `score(d) = Σ 1 / (60 + rank)` (1-based rank, `rrf_k = 60`); re-rank to top-5. Source: `src/hybrid_retrieval_eval.py`.
- **Weighted Fusion (this run):** BM25 top-20 ∪ Dense top-20 as candidates; min-max normalize each score within the candidate pool; combine as `0.85 × dense + 0.15 × BM25`; return top-5. Source: `src/final_retrieval_test.py`.
- **Cascade (this run):** if the query matches a section-number regex (`section|sec.?|§|ipc|bns|bnss|bsa` followed by a number), promote exact `section_number` matches to the front of the result list; fill remaining slots from dense ranking. Source: `src/final_retrieval_test.py`.
- All five methods use the same sample (n=1000, seed=42, k=5). Combined results are stored in `results/retrieval_eval.json`.

## Environment notes

| Item | Value |
|---|---|
| OS | macOS 26.6.1 (x86_64) |
| Python | 3.11.13 |
| pandas | 2.1.4 |
| numpy | 1.26.4 |
| rank-bm25 | 0.2.2 |
| scikit-learn | 1.8.0 |
| torch | 2.2.2 |
| sentence-transformers | 3.4.1 (pinned; not the latest 5.x) |
| transformers | 4.46.3 |
| huggingface-hub | 0.36.2 |
| embedding model | `all-MiniLM-L6-v2` |

Workarounds that affect reproducibility:

- The unpinned `pip install sentence-transformers` resolved to 5.7.0, which requires **PyTorch ≥ 2.5**. This machine has **torch 2.2.2**, so encoding failed until `sentence-transformers==3.4.1` and `transformers==4.46.3` were installed.
- Importing Transformers pulled in a TensorFlow build compiled for AVX; that aborted the process (`SIGABRT`) on this CPU. All dense-encoding runs used `TRANSFORMERS_NO_TF=1`, `TRANSFORMERS_NO_FLAX=1`, `USE_TF=0`, and `TOKENIZERS_PARALLELISM=false`.
- Dense encoding is CPU-only (no CUDA on this host). Exact floating-point values can differ slightly across hardware, but the evaluation sample and seed are fixed.

## Results table

Metrics at **k = 5**, **n = 1,000**. Best value per column in bold.

| Method | Precision@5 | Recall@5 | MRR | NDCG@5 |
|---|---:|---:|---:|---:|
| BM25 | 0.0724 | 0.362 | 0.2586 | 0.2844 |
| Dense (MiniLM) | 0.1190 | 0.595 | 0.4461 | 0.4833 |
| Hybrid (RRF, BM25+Dense) | 0.1134 | 0.567 | 0.3992 | 0.4409 |
| Weighted Fusion (0.85 dense / 0.15 BM25) | 0.1232 | 0.616 | 0.4817 | 0.5153 |
| Cascade (exact section + dense) | **0.1400** | **0.700** | **0.5238** | **0.5681** |

### Cascade trigger rate

| Metric | Value |
|---|---|
| `section_pattern_trigger_rate` | **0.226** (226 / 1,000 queries) |

On 22.6% of the sample the query contained an explicit section reference matching the cascade regex; the remaining 77.4% fell through to dense-only ranking. That is a substantial minority of the sample — enough that cascade’s gains are not based on a handful of triggered cases, but also not a majority of queries.

## Per-question-type breakdown table

Hit rate at k=5 (gold `chunk_id` in the top-5), by `question_type`. Best value per row in bold.

| Question type | BM25 | Dense | Hybrid RRF | Weighted Fusion | Cascade |
|---|---:|---:|---:|---:|---:|
| elements | 0.5079 | 0.6545 | 0.7068 | **0.7120** | 0.6859 |
| exceptions | 0.4459 | 0.7230 | 0.6622 | 0.7230 | **0.7703** |
| definitional_topic | 0.3133 | 0.6928 | 0.5904 | **0.7108** | 0.6928 |
| scenario | 0.3975 | 0.6211 | 0.6025 | **0.6335** | 0.6149 |
| definitional_section | 0.2343 | 0.4857 | 0.4686 | 0.5029 | **1.0000** |
| consequence | 0.2642 | 0.3962 | 0.3585 | 0.4088 | **0.4151** |

## Observations

- Across all four aggregate metrics, the ranking is: **Cascade > Weighted Fusion > Dense > Hybrid RRF > BM25**.
- Cascade is the overall winner: Recall@5 **0.700** (vs Dense 0.595, +0.105), MRR **0.5238** (vs Dense 0.4461, +0.078), NDCG@5 **0.5681** (vs Dense 0.4833, +0.085).
- Weighted Fusion is second overall and is the only fusion method that beats Dense-alone on every aggregate metric (Recall@5 0.616 vs 0.595; MRR 0.4817 vs 0.4461).
- Hybrid RRF remains below Dense on every aggregate metric, consistent with the previous audit.
- BM25 is last on every aggregate metric and every question type.
- Cascade’s largest per-type lift is on **definitional_section**, where hit rate reaches **1.000** (vs Dense 0.4857). That type of question explicitly names a section, so the short-circuit fires and places the correct chunk first.
- Cascade also leads on **exceptions** (0.7703) and **consequence** (0.4151), and ties Dense on **definitional_topic** (0.6928).
- Weighted Fusion leads on **elements** (0.7120), **definitional_topic** (0.7108), and **scenario** (0.6335) — the types where section numbers are less often named in the question text.
- Cascade underperforms Weighted Fusion on **elements** (0.6859 vs 0.7120) and **scenario** (0.6149 vs 0.6335).
- Cascade’s `section_pattern_trigger_rate` of **0.226** means roughly one in four sample queries carries an explicit section cue. The perfect `definitional_section` hit rate indicates those triggered cases are highly accurate when they fire; the remaining ~77% of queries still rely on the dense fallback.
- **consequence** remains the weakest question type for every method that uses dense retrieval (Dense 0.3962, Weighted Fusion 0.4088, Cascade 0.4151, Hybrid 0.3585).
- Precision@5 equals Recall@5 / 5 for every method, which follows from there being a single gold document per query.
