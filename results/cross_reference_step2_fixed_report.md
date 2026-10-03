# Fixed Cross-Reference Regex — Audit Report

## Objective
Re-measure relaxed recall@5 after fixing the cross-reference detector to catch plural
"sections X, Y and Z" lists (previous version only caught singular "section N").
Retrieval runs on the ORIGINAL, unaugmented corpus — Step 1's corpus-text-merging
approach has been dropped after it reduced strict recall in the prior run.

## Method
- Model: models/finetuned-bge-small-ipc-bns-e8 (unchanged)
- Eval set: data/splits/val.jsonl (n=635), test untouched
- Cross-reference detector: now matches both "section N" and "sections N, M and P" style lists

## Results

| Version | Sections w/ cross-refs | Strict Recall@5 | Relaxed Recall@5 | Extra hits |
|---|---:|---:|---:|---:|
| Previous (singular-only regex) | 319 | 0.8299 | 0.8425 | 8 |
| Fixed (singular + plural lists) | 339 | 0.8299 | 0.8441 | 9 |

## Observations
- Cross-reference detection coverage change: +20 sections (previously 319)
- Relaxed recall change vs previous fixed-regex attempt: +0.0016
- Strict recall should be unchanged or very close to the original 0.8299 baseline, since
  retrieval itself was not modified in this run — only the cross-reference map used for
  the relaxed metric changed.
