# Second Fine-tuning Audit Report

## Objective

Compare four fine-tuning epoch budgets (3, 5, 8, 15) for `BAAI/bge-small-en-v1.5` under the cascade retrieval protocol, using **proper val-then-single-test discipline**: all four configs are compared on `data/splits/val.jsonl` only; the winner (highest val NDCG@5) is confirmed on `data/splits/test.jsonl` **exactly once**. No config other than the winner is evaluated on the held-out test set in this run (except that epochs=3 already had a prior test number, reused only if it wins).

## Method

- **Corpus:** `data/clean/statutes.jsonl` (1,059 sections).
- **Splits (seed 42, fixed on disk):**
  - Train: `5083` → `data/splits/train.jsonl`
  - Val: `635` → `data/splits/val.jsonl` (model selection)
  - Test: `636` → `data/splits/test.jsonl` (final confirmation only)
- **Base model:** `BAAI/bge-small-en-v1.5`
- **Training pairs:** `5083` question ↔ gold statute text pairs from train
- **Loss:** `MultipleNegativesRankingLoss` (in-batch negatives)
- **Batch size:** 16
- **Warmup:** 10% of dataloader length
- **Configs trained / compared:**
  | Epochs | Model path | Trained in this run? |
  |---|---|---|
  | 3 | `models/finetuned-bge-small-ipc-bns` | No (prior run) |
  | 5 | `models/finetuned-bge-small-ipc-bns-e5` | Yes (unless already present) |
  | 8 | `models/finetuned-bge-small-ipc-bns-e8` | Yes (unless already present) |
  | 15 | `models/finetuned-bge-small-ipc-bns-e15` | Yes (unless already present) |
- **Retrieval protocol:** identical cascade (exact section-number short-circuit + dense fill) at **k = 5**
- **Selection rule:** highest **NDCG@5 on val**; test run only for the winner

## Environment notes

| Item | Value |
|---|---|
| OS | macOS 26.6.1 (x86_64) |
| Python | 3.11.13 (project `.venv`) |
| torch | 2.2.2 |
| sentence-transformers | 3.4.1 |
| transformers | 4.46.3 |
| device | CPU |
| wall-clock epochs=3 | 1008.0 s (16.8 min) |
| wall-clock epochs=5 | 1756.4 s (29.3 min) |
| wall-clock epochs=8 | 2129.2 s (35.5 min) |
| wall-clock epochs=15 | 3896.3 s (64.9 min) |

Workarounds: training ran in `.venv` (no TensorFlow) with `TRANSFORMERS_NO_TF=1`, `USE_TF=0`, `TORCHDYNAMO_DISABLE=1` because system TensorFlow 2.16.2 AVX-aborts this CPU.

## Validation comparison table

Metrics on **`data/splits/val.jsonl` only** (n=635, k=5). Best NDCG@5 in bold.

| Epochs | Precision@5 | Recall@5 | MRR | NDCG@5 |
|---|---:|---:|---:|---:|
| 3 | 0.1635 | 0.8173 | 0.6287 | 0.6764 |
| 5 | 0.1644 | 0.8220 | 0.6354 | 0.6824 |
| 8 | 0.1660 | 0.8299 | 0.6390 | **0.6871** |
| 15 | 0.1657 | 0.8283 | 0.6352 | 0.6840 |

**Selected winner:** epochs=**8** (highest val NDCG@5 = 0.6871).

**Val curve shape:** dropped after peaking at epoch 8 (val NDCG@5 at 15 = 0.6840 < peak 0.6871) — overfitting signal; winner is epochs=8, not 15

Chart: `results/epoch_comparison_val.png`

## Final test result

Definitive held-out test numbers for the **val-selected winner** (epochs=8), evaluated on `data/splits/test.jsonl` (n=636, k=5).

| Metric | Winner (epochs=8) on TEST |
|---|---:|
| Precision@5 | 0.1682 |
| Recall@5 | 0.8412 |
| MRR | 0.6547 |
| NDCG@5 | 0.7016 |
| Section trigger rate | 0.2233 |

Model path: `models/finetuned-bge-small-ipc-bns-e8`

Note: Single held-out test evaluation of the val-selected winner.

Prior epochs=3 test numbers (for comparison; only the winner’s test row above is the selection outcome):

| Metric | epochs=3 on TEST (prior) |
|---|---:|
| Precision@5 | 0.1642 |
| Recall@5 | 0.8208 |
| MRR | 0.6406 |
| NDCG@5 | 0.6861 |

## Per-question-type breakdown

Hit rate at k=5 on the **test** set: winning model vs prior epochs=3 test numbers.

| Question type | epochs=3 (test) | Winner epochs=8 (test) | Δ |
|---|---:|---:|---:|
| elements | 0.8411 | 0.8785 | +0.0374 |
| exceptions | 0.8246 | 0.8509 | +0.0263 |
| definitional_topic | 0.8571 | 0.8681 | +0.0110 |
| scenario | 0.7961 | 0.8350 | +0.0388 |
| definitional_section | 1.0000 | 1.0000 | +0.0000 |
| consequence | 0.5981 | 0.6075 | +0.0093 |

## Observations

- Val NDCG@5 by epochs: 3=0.6764, 5=0.6824, 8=0.6871, 15=0.6840.
- Winner selected by highest val NDCG@5: **epochs=8**.
- Curve characterization: **dropped after peaking at epoch 8 (val NDCG@5 at 15 = 0.6840 < peak 0.6871) — overfitting signal; winner is epochs=8, not 15**
- This answers “should we train more?” under the observed val evidence: the selected epoch count is 8, not automatically the largest budget.
- Final test NDCG@5 for the winner: **0.7016** (Recall@5 0.8412, MRR 0.6547).
- Relative to the prior epochs=3 test run: Δ NDCG@5 = +0.0155, Δ Recall@5 = +0.0204, Δ MRR = +0.0141.
- Only the winning config received a new (or reused-if-e3) test evaluation in this selection procedure; e5/e8/e15 were judged on val only.
- Training used 5083 pairs, batch size 16, MultipleNegativesRankingLoss, CPU.
