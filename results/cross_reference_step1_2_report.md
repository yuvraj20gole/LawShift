# Cross-Reference Augmentation & Relaxed Metric — Audit Report

## Objective
Measure two independent things on the SAME held-out validation set (n=635), never touching test:
1. Does enriching each statute chunk with its cross-referenced sections' text improve strict retrieval (Step 1)?
2. Does crediting cross-referenced retrievals as valid hits reveal a higher "true" effective accuracy (Step 2)?

## Method
- Model: models/finetuned-bge-small-ipc-bns-e8 (unchanged, no retraining in this step)
- Eval set: data/splits/val.jsonl (n=635) — test set untouched
- Cross-reference detection: regex match on "section N" within each section's own text, resolved against the same Act's section table
- Sections with at least one resolved cross-reference: 319 / 1059

## Results

| Corpus version | Strict Recall@5 | Relaxed Recall@5 | Additional hits credited by relaxed metric |
|---|---:|---:|---:|
| Original (unaugmented) | 0.8299 | 0.8425 | 8 |
| Augmented (cross-refs merged into chunk text) | 0.8079 | 0.8142 | 4 |

## Observations
- Step 1 impact (strict recall, original vs augmented corpus): -0.0220
- Step 2 impact (relaxed vs strict, on original corpus): +0.0126
- Both strict and relaxed numbers are reported here deliberately — the paper should present both, not just the higher one.
