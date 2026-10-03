# Combined GSMS-B + GovIntel Training — Audit Report

## Objective

Compare three combined-data fine-tunes (GSMS-B train + GovIntel extracted pairs, epochs 3/5/8) against the previous best GSMS-B-only model (`models/finetuned-bge-small-ipc-bns-e8`) on `data/splits/val.jsonl` only, then confirm the val-selected winner on `data/splits/test.jsonl` exactly once.

## Method

- **Pair counts by source:** 5,083 GSMS-B (`data/splits/train.jsonl`) + 4,038 GovIntel (`data/clean/govintel_extracted_v2.jsonl`) = **9,121** combined training pairs. Original-e8 used the 5,083 GSMS-B pairs only.
- **Val / test:** 635 / 636 rows from `data/splits/` (fixed seed-42 split; not mixed with GovIntel).
- **Base model (combined runs):** `BAAI/bge-small-en-v1.5`, trained from scratch each time.
- **Hyperparameters (same as prior GSMS-B fine-tunes):** `MultipleNegativesRankingLoss`; example format `[question, gold statute text]`; batch size 16; warmup = 10% of dataloader length (57 steps); epochs in {3, 5, 8}.
- **Retrieval protocol:** identical cascade as every prior round — exact section-number short-circuit, then dense fill from the bi-encoder; k=5.
- **Selection:** highest val NDCG@5 among original-e8, combined-e3, combined-e5, combined-e8. If original-e8 wins, reuse `results/final_selected_model_test_eval.json` rather than re-running test.

## Environment notes

| Item | Value |
|---|---|
| device | CPU |
| sentence-transformers | 3.4.1 |
| torch | 2.2.2 |
| wall-clock combined-e3 | 1444.8 s (24.1 min) |
| wall-clock combined-e5 | 2392.1 s (39.9 min) |
| wall-clock combined-e8 | 3719.4 s (62.0 min) |

Val metrics for all four configs were produced with the same cascade evaluator as `src/finetune_more.py` / `src/finetune_combined.py`. Combined val files: `results/combined_val_e3.json`, `results/combined_val_e5.json`, `results/combined_val_e8.json`. Original-e8 val: `results/val_eval_epochs8.json`.

## Validation comparison table

Metrics on **`data/splits/val.jsonl` only** (n=635, k=5). Best NDCG@5 in bold.

| Config | Precision@5 | Recall@5 | MRR | NDCG@5 |
|---|---:|---:|---:|---:|
| original-e8 (GSMS-B only) | 0.1660 | 0.8299 | 0.6390 | **0.6871** |
| combined-e3 | 0.1587 | 0.7937 | 0.5913 | 0.6423 |
| combined-e5 | 0.1603 | 0.8016 | 0.6130 | 0.6605 |
| combined-e8 | 0.1600 | 0.8000 | 0.6053 | 0.6544 |

**Selected winner:** **original-e8** (highest val NDCG@5 = 0.6871). Combined-e5 is the best combined config on val (NDCG@5 0.6605) but still below original-e8.

## Final test result

Because original-e8 won on val, the existing test file was reused (`results/final_selected_model_test_eval.json`); test was not re-run.

| Metric | original-e8 TEST (reused) | Winner (original-e8) TEST |
|---|---:|---:|
| Recall@5 | 0.8412 | 0.8412 |
| MRR | 0.6547 | 0.6547 |
| NDCG@5 | 0.7016 | 0.7016 |
| Precision@5 | 0.1682 | 0.1682 |

Rounded to the figures given for the previous best: Recall@5 **0.841**, MRR **0.655**, NDCG@5 **0.702**. Δ vs that baseline is **0** on every metric.

## Per-question-type breakdown (TEST)

Hit rate at k=5. Winner is original-e8, so deltas are zero.

| Question type | original-e8 TEST | Winner (original-e8) TEST | Δ |
|---|---:|---:|---:|
| elements | 0.8785 | 0.8785 | +0.0000 |
| exceptions | 0.8509 | 0.8509 | +0.0000 |
| definitional_topic | 0.8681 | 0.8681 | +0.0000 |
| scenario | 0.8350 | 0.8350 | +0.0000 |
| definitional_section | 1.0000 | 1.0000 | +0.0000 |
| consequence | 0.6075 | 0.6075 | +0.0000 |

## Observations

- On val, original-e8 is first on all four aggregate metrics (Recall@5 0.8299, MRR 0.6390, NDCG@5 0.6871).
- Among combined-data runs, val NDCG@5 is 0.6423 (e3), 0.6605 (e5), 0.6544 (e8): it rises from 3→5 epochs and drops from 5→8.
- The best combined config (e5) is 0.0266 NDCG@5 below original-e8 on val (0.6605 vs 0.6871) and 0.0283 Recall@5 below (0.8016 vs 0.8299).
- Adding 4,038 GovIntel pairs to the 5,083 GSMS-B pairs did not produce a val NDCG@5 above the GSMS-B-only e8 model.
- Test was not re-run; the val winner is original-e8, whose held-out test numbers remain Recall@5 0.8412, MRR 0.6547, NDCG@5 0.7016.
