# Retrieval Audit Report

## Objective

Measure whether Reciprocal Rank Fusion of BM25 and dense MiniLM retrieval outperforms either method alone at recovering the gold statute `chunk_id` for a held-out sample of legal QA questions.

## Method

- **Corpus:** `data/clean/statutes.jsonl` (1,059 sections from BNS / BNSS / BSA 2023).
- **Queries:** `data/clean/qa_eval_ready.jsonl`; a random sample of **n = 1,000** questions, `random_state` / seed **42**.
- **Gold label:** the QA row’s `chunk_id` (exactly one relevant document per query).
- **k:** 5 (Precision@5, Recall@5, MRR, NDCG@5; NDCG uses a binary relevance gain of 1 at the gold rank).
- **BM25:** `rank_bm25.BM25Okapi` on whitespace-tokenized lowercase statute text; top-k by BM25 score.
- **Dense:** `sentence-transformers` model `all-MiniLM-L6-v2`; cosine similarity of the question embedding against precomputed corpus embeddings; top-k.
- **Hybrid (this run):** for each query, take BM25 top-20 and dense top-20 independently; fuse with RRF, `score(d) = Σ 1 / (60 + rank)` over lists that contain `d` (1-based rank, `rrf_k = 60`); re-rank and return top-5.
- BM25 and Dense numbers are from the prior `src/retrieval_eval.py` run on the same sample protocol (n=1000, k=5, seed=42). Hybrid numbers are from `src/hybrid_retrieval_eval.py`. Combined results are stored in `results/retrieval_eval.json`.

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
- Importing Transformers pulled in a TensorFlow build compiled for AVX; that aborted the process (`SIGABRT`) on this CPU. Both eval runs used `TRANSFORMERS_NO_TF=1`, `TRANSFORMERS_NO_FLAX=1`, `USE_TF=0`, and `TOKENIZERS_PARALLELISM=false`.
- Dense encoding is CPU-only (no CUDA on this host). Exact floating-point values can differ slightly across hardware, but the evaluation sample and seed are fixed.

## Results table

Metrics at **k = 5**, **n = 1,000**.

| Method | Precision@5 | Recall@5 | MRR | NDCG@5 |
|---|---:|---:|---:|---:|
| BM25 | 0.0724 | 0.362 | 0.2586 | 0.2844 |
| Dense (MiniLM) | **0.1190** | **0.595** | **0.4461** | **0.4833** |
| Hybrid (RRF, BM25+Dense) | 0.1134 | 0.567 | 0.3992 | 0.4409 |

## Per-question-type breakdown table

Hit rate at k=5 (gold `chunk_id` in the top-5), by `question_type`.

| Question type | BM25 | Dense (MiniLM) | Hybrid (RRF) |
|---|---:|---:|---:|
| elements | 0.5079 | 0.6545 | **0.7068** |
| exceptions | 0.4459 | **0.7230** | 0.6622 |
| definitional_topic | 0.3133 | **0.6928** | 0.5904 |
| scenario | 0.3975 | **0.6211** | 0.6025 |
| definitional_section | 0.2343 | **0.4857** | 0.4686 |
| consequence | 0.2642 | **0.3962** | 0.3585 |

## Observations

- On all four aggregate metrics, Dense is first, Hybrid second, BM25 third. Hybrid sits closer to Dense than to BM25 (Recall@5: Dense 0.595, Hybrid 0.567, BM25 0.362).
- Relative to Dense, Hybrid is lower by 0.028 Recall@5, 0.047 MRR, and 0.042 NDCG@5. Relative to BM25, Hybrid is higher by 0.205 Recall@5, 0.141 MRR, and 0.156 NDCG@5.
- Fusing BM25 into Dense via RRF does not raise the overall scores above Dense-alone.
- By question type, Hybrid beats Dense on **elements** only (0.7068 vs 0.6545). Dense is highest on the other five types.
- BM25 is lowest on every question type.
- For BM25, the highest hit rate is **elements** (0.5079) and the lowest is **definitional_section** (0.2343).
- For Dense, the highest hit rate is **exceptions** (0.7230) and the lowest is **consequence** (0.3962).
- For Hybrid, the highest hit rate is **elements** (0.7068) and the lowest is **consequence** (0.3585).
- **consequence** is the weakest type for both Dense and Hybrid; **definitional_section** is the weakest for BM25 and the second-weakest for Dense and Hybrid.
- Precision@5 is Recall@5 / 5 for every method, which follows from there being a single gold document per query.
