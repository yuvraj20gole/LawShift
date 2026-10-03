# Combined GSMS-B + GovIntel Fine-tuning — Audit Report

## Objective

Test whether adding 4038 GovIntel question–section pairs to the 5083 GSMS-B training pairs improves cascade retrieval over the previous best model (`models/finetuned-bge-small-ipc-bns-e8`), using val-then-single-test discipline.

## Method

- **Base model:** `BAAI/bge-small-en-v1.5` (fresh start for combined runs)
- **Training pairs:** 5083 GSMS-B (`data/splits/train.jsonl`) + 4038 GovIntel (`data/clean/govintel_extracted_v2.jsonl`) = **9121**
- **Val / test:** `635` / `636` from `data/splits/` (unchanged; GovIntel was contamination-checked against nyaya-eval, not this split)
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
| wall-clock combined-e3 | 1444.8 s (24.1 min) |
| wall-clock combined-e5 | 2392.1 s (39.9 min) |
| wall-clock combined-e8 | 3719.4 s (62.0 min) |

## Validation comparison table

Metrics on **`data/splits/val.jsonl` only** (n=635, k=5). Best NDCG@5 in bold.

| Config | Precision@5 | Recall@5 | MRR | NDCG@5 |
|---|---:|---:|---:|---:|
| original-e8 | 0.1660 | 0.8299 | 0.6390 | **0.6871** |
| combined-e3 | 0.1587 | 0.7937 | 0.5913 | 0.6423 |
| combined-e5 | 0.1603 | 0.8016 | 0.6130 | 0.6605 |
| combined-e8 | 0.1600 | 0.8000 | 0.6053 | 0.6544 |

**Selected winner:** **original-e8** (val NDCG@5 = 0.6871).

## Final test result

| Metric | Previous best (original-e8 TEST) | Winner (original-e8) TEST |
|---|---:|---:|
| Precision@5 | 0.1682 | 0.1682 |
| Recall@5 | 0.8412 | 0.8412 |
| MRR | 0.6547 | 0.6547 |
| NDCG@5 | 0.7016 | 0.7016 |

Note: Reused existing original-e8 test evaluation; no second test run.

## Per-question-type breakdown (TEST)

| Question type | original-e8 TEST | Winner (original-e8) TEST | Δ |
|---|---:|---:|---:|
| elements | 0.8785 | 0.8785 | +0.0000 |
| exceptions | 0.8509 | 0.8509 | +0.0000 |
| definitional_topic | 0.8681 | 0.8681 | +0.0000 |
| scenario | 0.8350 | 0.8350 | +0.0000 |
| definitional_section | 1.0000 | 1.0000 | +0.0000 |
| consequence | 0.6075 | 0.6075 | +0.0000 |

## Observations

- Val NDCG@5: original-e8=0.6871, combined-e3=0.6423, combined-e5=0.6605, combined-e8=0.6544.
- Combined-run val NDCG@5 by epochs 3/5/8: 0.6423 / 0.6605 / 0.6544.
- Winner by val NDCG@5: **original-e8**.
- Test NDCG@5 for the winner: 0.7016 (previous best original-e8: 0.7016; Δ +0.0000).
- Test Recall@5 Δ vs original-e8: +0.0000; MRR Δ: +0.0000.
- Training used 9121 pairs (no hard negatives), batch size 16, MultipleNegativesRankingLoss, CPU.
- Only the val-selected winner received a new test evaluation (or a reuse of original-e8's existing test file).
