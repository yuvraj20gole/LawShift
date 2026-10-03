# Fine-tuning Audit Report

## Objective

Measure whether contrastive fine-tuning of `BAAI/bge-small-en-v1.5` on IPC/BNS QA–statute pairs improves cascade retrieval (exact section short-circuit + dense) on a held-out test split that was never used during training.

## Method

- **Corpus:** `data/clean/statutes.jsonl` (1,059 sections from BNS / BNSS / BSA 2023).
- **QA split (seed 42, shuffled once, saved to disk):**
  - Train: `5083` rows → `data/splits/train.jsonl`
  - Val: `635` rows → `data/splits/val.jsonl` (held out; not used in this run)
  - Test: `636` rows → `data/splits/test.jsonl`
- **Base embedding model:** `BAAI/bge-small-en-v1.5`
- **Fine-tuning:**
  - Loss: `MultipleNegativesRankingLoss` (in-batch negatives)
  - Training pairs: question ↔ gold statute text for each train row (`5083` pairs)
  - Epochs: `3`
  - Batch size: `16`
  - Warmup steps: `31` (10% of steps per epoch × dataloader length)
  - Output: `models/finetuned-bge-small-ipc-bns`
- **Retrieval protocol (before and after):** identical cascade from `src/final_retrieval_test.py` — if the query matches a section-number regex, promote exact `section_number` matches; fill remaining top-k slots from dense cosine ranking. Evaluated at **k = 5** on **`data/splits/test.jsonl` only**.
- **Context row:** Cascade + MiniLM numbers are from the earlier experiment on a random n=1000 sample of the full QA set (seed 42), not the held-out test split — included for context only, not a fair comparison.

## Environment notes

| Item | Value |
|---|---|
| OS | macOS 26.6.1 (x86_64) |
| Python | 3.11.13 |
| pandas | 2.1.4 |
| numpy | 1.26.4 |
| scikit-learn | 1.8.0 |
| torch | 2.2.2 |
| sentence-transformers | 3.4.1 |
| transformers | 4.46.3 |
| base model | BAAI/bge-small-en-v1.5 |
| fine-tuned model path | models/finetuned-bge-small-ipc-bns |
| fine-tuning wall-clock | 1008.0 s (16.8 min) |

Workarounds that affect reproducibility:

- `sentence-transformers` pinned to **3.4.1** because newer releases require PyTorch ≥ 2.5 (this machine has 2.2.2).
- The system Python had TensorFlow 2.16.2 built for AVX; importing it aborts this CPU. Fine-tuning therefore ran inside the project virtualenv `.venv` (PyTorch-only; no TensorFlow installed).
- Dense encoding / training used `TRANSFORMERS_NO_TF=1`, `TRANSFORMERS_NO_FLAX=1`, `USE_TF=0`, `TOKENIZERS_PARALLELISM=false`, and `TORCHDYNAMO_DISABLE=1`.
- Training and encoding ran on CPU only (no CUDA).
- Extra dependency required for `SentenceTransformer.fit` under ST 3.4.1: `accelerate>=0.26.0` (and `datasets`).

## Results table

| Method | Eval set | Precision@5 | Recall@5 | MRR | NDCG@5 | Trigger rate |
|---|---|---:|---:|---:|---:|---:|
| Cascade + MiniLM (original, context only) | random n=1000 of full QA | 0.1400 | 0.7000 | 0.5238 | 0.5681 | 0.2260 |
| Cascade + bge-small (before fine-tuning) | held-out test split (n=636) | 0.1340 | 0.6698 | 0.5096 | 0.5499 | 0.2233 |
| Cascade + bge-small (after fine-tuning) | held-out test split (n=636) | 0.1642 | 0.8208 | 0.6406 | 0.6861 | 0.2233 |

**Note:** Row 1 used a different evaluation sample (non-held-out random draw from the full QA set). Rows 2 and 3 are the only apples-to-apples comparison: same cascade protocol, same `data/splits/test.jsonl`.

Chart: `results/finetuning_comparison.png` (Before vs After on the held-out test split).

## Per-question-type breakdown table

Hit rate at k=5 on the held-out test split, before vs after fine-tuning.

| Question type | Before (bge-small) | After (fine-tuned) | Δ (after − before) |
|---|---:|---:|---:|
| elements | 0.6916 | 0.8411 | +0.1495 |
| exceptions | 0.6667 | 0.8246 | +0.1579 |
| definitional_topic | 0.6923 | 0.8571 | +0.1648 |
| scenario | 0.5243 | 0.7961 | +0.2718 |
| definitional_section | 1.0000 | 1.0000 | +0.0000 |
| consequence | 0.4206 | 0.5981 | +0.1776 |

For context only — Cascade + MiniLM hit rates on the earlier n=1000 full-QA sample (not the held-out test split):

| Question type | Cascade + MiniLM (context) |
|---|---:|
| elements | 0.6859 |
| exceptions | 0.7703 |
| definitional_topic | 0.6928 |
| scenario | 0.6149 |
| definitional_section | 1.0000 |
| consequence | 0.4151 |

## Observations

- On the held-out test split, fine-tuning changes aggregate metrics by: Precision@5 +0.0302, Recall@5 +0.1509, MRR +0.1311, NDCG@5 +0.1362.
- Before fine-tuning (Cascade + off-the-shelf bge-small) on the test split: Recall@5 0.6698, MRR 0.5096, NDCG@5 0.5499.
- After fine-tuning (Cascade + fine-tuned bge-small) on the same test split: Recall@5 0.8208, MRR 0.6406, NDCG@5 0.6861.
- Section-pattern trigger rate on the test split: before 0.2233, after 0.2233 (same cascade regex; rates should be essentially identical).
- Largest per-type hit-rate change (after − before): **scenario** (+0.2718).
- Smallest (most negative / least positive) per-type hit-rate change: **definitional_section** (+0.0000).
- Cascade + MiniLM on the earlier non-held-out sample had Recall@5 0.7000; that figure is not directly comparable to the bge-small test-split numbers above.
- Training used 5083 question–statute pairs, 3 epochs, batch size 16, MultipleNegativesRankingLoss, wall-clock 16.8 minutes on CPU.
- Precision@5 equals Recall@5 / 5 for each cascade run, which follows from a single gold document per query.
