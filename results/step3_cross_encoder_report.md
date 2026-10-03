# Cross-Encoder Re-ranking — Audit Report (Off-the-shelf, No Fine-tuning)

## Objective
Test whether re-ranking the bi-encoder's top-30 candidates with a pretrained
cross-encoder (not fine-tuned on our data) improves retrieval, before investing
time in fine-tuning a cross-encoder on our own training data.

## Method
- Bi-encoder: models/finetuned-bge-small-ipc-bns-e8 (retrieves top-30 candidate pool)
- Cross-encoder: cross-encoder/ms-marco-MiniLM-L-6-v2 (off-the-shelf, general-domain, NOT fine-tuned on IPC/BNS data)
- Eval set: data/splits/val.jsonl (n=635), test untouched
- k = 5 for final results in both conditions

## Results

| Method | Recall@5 | MRR | NDCG@5 |
|---|---:|---:|---:|
| Bi-encoder only (baseline) | 0.8299 | 0.6390 | 0.6871 |
| + Cross-encoder rerank (off-the-shelf) | 0.7717 | 0.6340 | 0.6684 |

## Per-question-type breakdown

| Question type | Baseline | Reranked | Delta |
|---|---:|---:|---:|
| scenario | 0.7899 | 0.6555 | -0.1345 |
| consequence | 0.7000 | 0.6600 | -0.0400 |
| definitional_topic | 0.9286 | 0.8304 | -0.0982 |
| elements | 0.7300 | 0.7300 | +0.0000 |
| definitional_section | 1.0000 | 1.0000 | +0.0000 |
| exceptions | 0.8252 | 0.7670 | -0.0583 |

## Observations
- Overall Recall@5 change from re-ranking: -0.0583
- Overall NDCG@5 change: -0.0187
- This cross-encoder has NOT been fine-tuned on legal/IPC/BNS data — it is a general
  passage-relevance model. A positive result here means the approach is worth fine-tuning
  further; a flat or negative result means off-the-shelf domain mismatch is limiting it,
  and fine-tuning the cross-encoder on our training pairs should be tried before abandoning
  this direction.
