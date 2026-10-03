# Hard-Negative Fine-tuning — Audit Report

## Objective

Test whether adding explicit hard negatives (same-chapter sections plus the current model's own near-misses) improves cascade retrieval over the previous best model (`models/finetuned-bge-small-ipc-bns-e8`), using **val-then-single-test** discipline: compare original-e8, hardneg-e3, and hardneg-e8 on `data/splits/val.jsonl` only; evaluate the winner on `data/splits/test.jsonl` exactly once (reuse the existing original-e8 test file if that config wins).

## Method

- **Base model:** `BAAI/bge-small-en-v1.5` (fresh start for hardneg runs; original-e8 is the prior winner without hard negatives)
- **Train / val / test:** `5083` / `635` / `636` from `data/splits/`
- **Loss:** `MultipleNegativesRankingLoss`; each example is `[question, gold_statute, hard_neg, ...]` so extra texts are example-specific in-batch negatives
- **Batch size:** 16; warmup 10% of dataloader length
- **Hard-negative mining (train only):**
  - Same-chapter / same-act: up to 2 neighbors of the gold `chunk_id`
  - Embedding-mined from `models/finetuned-bge-small-ipc-bns-e8`: up to 2 near-misses from the top-10 (excluding gold)
  - Combined, deduped, capped at 3 per example
- **Mining coverage:** 5083 / 5083 examples have ≥1 hard negative
- **Average negatives per example:** same-chapter 1.986; embedding-mined 2.000; after cap 2.980
- **Retrieval protocol:** identical cascade (exact section-number short-circuit + dense fill), k=5
- **Selection:** highest val NDCG@5 among original-e8, hardneg-e3, hardneg-e8

## Environment notes

| Item | Value |
|---|---|
| OS | macOS (x86_64), CPU |
| Python | 3.11 (project `.venv`) |
| torch | 2.2.2 |
| sentence-transformers | 3.4.1 |
| wall-clock hardneg-e3 | 2239.6 s (37.3 min) |
| wall-clock hardneg-e8 | 6341.6 s (105.7 min) |

Training used `TRANSFORMERS_NO_TF=1`, `USE_TF=0`, `TORCHDYNAMO_DISABLE=1`.

## Validation comparison table

Metrics on **`data/splits/val.jsonl` only** (n=635, k=5). Best NDCG@5 in bold.

| Config | Precision@5 | Recall@5 | MRR | NDCG@5 |
|---|---:|---:|---:|---:|
| original-e8 | 0.1660 | 0.8299 | 0.6390 | **0.6871** |
| hardneg-e3 | 0.1591 | 0.7953 | 0.6003 | 0.6493 |
| hardneg-e8 | 0.1594 | 0.7969 | 0.6044 | 0.6528 |

**Selected winner:** **original-e8** (val NDCG@5 = 0.6871).

## Final test result

Held-out test for the val-selected winner (`original-e8`), vs previous best original-e8 test (Recall@5 0.841, MRR 0.655, NDCG@5 0.702).

| Metric | Previous best (original-e8 TEST) | Winner (original-e8) TEST |
|---|---:|---:|
| Precision@5 | 0.1682 | 0.1682 |
| Recall@5 | 0.8412 | 0.8412 |
| MRR | 0.6547 | 0.6547 |
| NDCG@5 | 0.7016 | 0.7016 |

Note: Reused existing original-e8 test evaluation; no second test run.

## Per-question-type breakdown (TEST)

Hit rate at k=5: original-e8 vs winner. `elements` and `definitional_topic` were the “clearly wrong” categories called out in earlier error analysis.

| Question type | original-e8 TEST | Winner (original-e8) TEST | Δ |
|---|---:|---:|---:|
| elements ← earlier error-analysis focus | 0.8785 | 0.8785 | +0.0000 |
| exceptions | 0.8509 | 0.8509 | +0.0000 |
| definitional_topic ← earlier error-analysis focus | 0.8681 | 0.8681 | +0.0000 |
| scenario | 0.8350 | 0.8350 | +0.0000 |
| definitional_section | 1.0000 | 1.0000 | +0.0000 |
| consequence | 0.6075 | 0.6075 | +0.0000 |

- `elements` test hit-rate change: +0.0000
- `definitional_topic` test hit-rate change: +0.0000

## Observations

- Val NDCG@5: original-e8=0.6871, hardneg-e3=0.6493, hardneg-e8=0.6528.
- Winner by val NDCG@5: **original-e8**.
- Test NDCG@5 for the winner: 0.7016 (previous best original-e8: 0.7016; Δ +0.0000).
- Test Recall@5 Δ vs original-e8: +0.0000; MRR Δ: +0.0000.
- Hard-negative training used 5083 examples, batch size 16, MultipleNegativesRankingLoss, CPU.
- Only the val-selected winner received a new test evaluation (or a reuse of original-e8's existing test file).
