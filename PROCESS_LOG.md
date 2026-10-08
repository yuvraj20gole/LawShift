# Process Log — IPC/BNS Retrieval Sprint

Internal research journal. Numbers below are taken from `results/*.json` and `results/*.md` unless a gap is called out. This is not the paper.

Environment that applied to almost every ML run: macOS x86_64, Python 3.11, project `.venv`, CPU only, `sentence-transformers==3.4.1`, `transformers==4.46.3`, `torch==2.2.2`. System TensorFlow 2.16.2 AVX-aborts this CPU, so runs used `TRANSFORMERS_NO_TF=1 TRANSFORMERS_NO_FLAX=1 USE_TF=0 TOKENIZERS_PARALLELISM=false TORCHDYNAMO_DISABLE=1`.

---

## 1. Dataset Discovery & Verification

This section was a manual search across tools, not a scripted report. There is no `results/` file that lists rejected candidates. What follows is the working record of what was kept.

**Core four used from the start**

- GSMS-B statutes → `data/clean/statutes.jsonl`. After cleaning (`results/statutes_qa_cleaning_report.json`): **1059** rows (BNSS 531, BNS 358, BSA 170).
- GSMS-B QA → `data/clean/qa_eval_ready.jsonl`: **6354** rows, six question types × 1059 sections.
- IPC–BNS mapping (`nandhakumarg/IPC_and_BNS_transformation`) → `data/clean/mapping.jsonl`: **562** usable rows after cleaning (`results/mapping_cleaning_report.json`).
- ILDC: used as a named source in the original project framing. No ILDC row counts, splits, or eval numbers exist in `results/`.

**New candidates**

- **GovIntel** (`aashnasharma/govintel-legal-dataset`): verified real. `results/govintel_extraction_v2_report.json` records **12,859** `train.jsonl` records. The figure “14,280 rows” does not appear in any `results/` file; 12,859 is the count this repo actually processed.
- **nyaya-eval-v0** (`NyayaLabs98/nyaya-eval-v0`): verified real. `results/govintel_contamination_check.json` has `nyaya_eval_filtered_count`: **185** (BNS/BNSS/BSA filter of the test split).
- **IL-TUR, InLegalNER, BNS_detailed, BNS_definitions**: verified in the discovery pass and deprioritized (cost / mismatch). No quantitative rejection reports were saved.

**Correction: nyaya-eval-v0 was briefly treated as fabricated.** A web search miss was read as “this dataset does not exist.” Direct Hugging Face fetch (`src/extract_govintel_and_check_contamination.py` loads `NyayaLabs98/nyaya-eval-v0`, split `test`) proved it real. Web-search failure ≠ nonexistence. That correction is why nyaya later became the external validation set.

**GovIntel vs our mapping (novelty).** `src/inspect_govintel_ipc_temporal.py` was written to inspect graph edges. The working conclusion: GovIntel `IPC_TEMPORAL_PAIR` edges are bare node-ID pairs (no section text), while `mapping.jsonl` is a citable table with IPC/BNS headings and descriptions. The “512 edges” count is **not** stored in any `results/*.json`; it came from that inspection run. Novelty of the mapping table as a descriptive resource still holds: we did not replace it with GovIntel’s graph.

---

## 2. Data Cleaning

`results/cleaning_report.json` **does not exist**. Cleaning numbers are in the two files below.

**Statutes / QA** (`results/statutes_qa_cleaning_report.json`)

| | Before | After | Dropped |
|---|---:|---:|---:|
| Statutes | 1059 | 1059 | null text 0, duplicate `chunk_id` 0 |
| QA | 6354 | 6354 | null 0, duplicates 0 |

QA `chunk_id` mismatches vs statutes: **0** (rate **0.0**). Six question types, 1059 each: `definitional_topic`, `definitional_section`, `scenario`, `elements`, `exceptions`, `consequence`.

Splits (seed 42, recorded in the fine-tuning reports): train **5083**, val **635**, test **636**.

**Mapping** (`results/mapping_cleaning_report.json`)

- Raw rows: **563**. Junk dropped: **1** (`ipc_section` = `"Repealed"`). Final: **562**.
- `mapping_type` counts: **section 294**, **partial 122**, **merged 117**, **dropped 29**.
- Merged groups (several IPC sections pointing at the same raw BNS string): **40**.

---

## 3. Retrieval Method Search

Source: `results/retrieval_eval.json`, `results/final_retrieval_audit_report.md`.

Protocol: corpus 1059 statutes; **n = 1000** QA sample, seed 42; k = 5; gold = `chunk_id`. MiniLM = `all-MiniLM-L6-v2`.

| Method | P@5 | Recall@5 | MRR | NDCG@5 |
|---|---:|---:|---:|---:|
| BM25 | 0.0724 | 0.362 | 0.2586 | 0.2844 |
| Dense (MiniLM) | 0.1190 | 0.595 | 0.4461 | 0.4833 |
| Hybrid RRF (BM25+Dense, rrf_k=60) | 0.1134 | 0.567 | 0.3992 | 0.4409 |
| Weighted fusion (0.85 dense / 0.15 BM25) | 0.1232 | 0.616 | 0.4817 | 0.5153 |
| **Cascade** (exact section + dense) | **0.1400** | **0.700** | **0.5238** | **0.5681** |

Ranking: Cascade > Weighted Fusion > Dense > Hybrid RRF > BM25.

**Why naive RRF lost.** RRF sat **below Dense on every aggregate metric**. Reciprocal-rank fusion of BM25 top-20 ∪ Dense top-20 diluted a stronger dense ranking with a much weaker lexical ranker. Weighted fusion (dense-heavy) did beat Dense (Recall@5 0.616 vs 0.595). Cascade won overall because 22.6% of queries name a section (`section_pattern_trigger_rate` 0.226); `definitional_section` hit rate went to **1.000** vs Dense 0.486. Cascade still trailed weighted fusion on `elements` (0.686 vs 0.712) and `scenario` (0.615 vs 0.634). `consequence` was the hardest type for every dense method (Cascade 0.415).

Locked retrieval protocol for the rest of the sprint: cascade, k=5.

---

## 4. Fine-Tuning Search

Sources: `results/finetuning_audit_report.md`, `results/second_finetuning_audit_report.md`, `results/final_selected_model_test_eval.json`.

Base model swapped from MiniLM to **`BAAI/bge-small-en-v1.5`**. Loss: MultipleNegativesRankingLoss, batch 16, question ↔ gold statute text, 5083 train pairs.

**First fine-tune (3 epochs)** on held-out test (n=636), same cascade:

| | Recall@5 | MRR | NDCG@5 |
|---|---:|---:|---:|
| Cascade + off-the-shelf bge-small | 0.6698 | 0.5096 | 0.5499 |
| Cascade + fine-tuned (3 ep) | 0.8208 | 0.6406 | 0.6861 |

Trigger rate unchanged at 0.2233. Biggest type lift: `scenario` +0.272.

**Epoch sweep on val only** (n=635), then test once for the winner:

| Epochs | Val Recall@5 | Val MRR | Val NDCG@5 |
|---|---:|---:|---:|
| 3 | 0.8173 | 0.6287 | 0.6764 |
| 5 | 0.8220 | 0.6354 | 0.6824 |
| **8** | **0.8299** | **0.6390** | **0.6871** |
| 15 | 0.8283 | 0.6352 | 0.6840 |

Epoch 15 dropped below 8 on val NDCG (0.6840 < 0.6871) — overfitting. Winner: **`models/finetuned-bge-small-ipc-bns-e8`**.

**Locked test numbers** (`results/final_selected_model_test_eval.json`, n=636, k=5): Recall@5 **0.8412**, MRR **0.6547**, NDCG@5 **0.7016**, P@5 0.1682, trigger 0.2233. Rounded as used later: Recall@5 0.841, MRR 0.655, NDCG@5 0.702.

This model is “original-e8” everywhere below. Test was not re-run for later losers.

---

## 5. Error Analysis

`results/error_analysis_sample.md` header: **108 misses / 635 val (17.0% miss rate)** under original-e8 cascade. Twenty misses were sampled for manual review (stratified by question type in `src/error_analysis.py`).

The sample file still has **empty judgment checkboxes**. The tally **7 defensible / 4 ambiguous / 9 clearly wrong is not stored in any `results/*.json` and was never filled into the markdown.** It is the working count from that review session.

What *is* visible in the sample, and what drove the next experiment: several “misses” retrieve a section that the gold text itself points to. Miss 1 is the type case — gold `BNSS_411` (difference of opinion on death-sentence confirmation) tells the reader to apply **section 433**; the model’s top hit is `BNSS_433`. That is the **cross-reference defensible-miss** pattern: strict `chunk_id` match is wrong, legally the retrieved section is what the gold tells you to use.

`definitional_section` had 0 misses in the e8 val/test type tables (hit rate 1.0). `consequence` stayed hardest (test hit rate 0.6075).

---

## 6. Four Failed Improvement Attempts

Negative results. Each was selected against original-e8 on **val only**. None beat val NDCG@5 0.6871. Test was not re-opened except to reuse e8’s existing test file. That is useful: it bounds what “just add X” does on this task.

### 6a. Cross-reference corpus augmentation (then relaxed metric)

`results/cross_reference_step1_2_report.md`, `results/cross_reference_step2_fixed_report.md`.

Merging cross-referenced section text into the retrieval corpus **hurt** strict val Recall@5: **0.8299 → 0.8079** (−0.022). Dropped.

Relaxed metric (credit gold’s explicit cross-refs, original corpus, no retrieval change):

| Detector | Sections w/ refs | Strict R@5 | Relaxed R@5 | Extra hits |
|---|---:|---:|---:|---:|
| Singular “section N” only | 319 / 1059 | 0.8299 | 0.8425 | 8 |
| Singular + plural lists | 339 / 1059 | 0.8299 | 0.8441 | 9 |

Plural-list regex added 20 sections and +1 extra hit. Relaxed recall is a **reporting** number, not a better retriever. Map kept as `data/clean/cross_ref_map.json` for later stages, not for the corpus.

### 6b. Off-the-shelf cross-encoder rerank

`results/step3_cross_encoder_report.md`. e8 retrieves top-30; `cross-encoder/ms-marco-MiniLM-L-6-v2` reranks to k=5. Val n=635.

| | Recall@5 | MRR | NDCG@5 |
|---|---:|---:|---:|
| Bi-encoder only | 0.8299 | 0.6390 | 0.6871 |
| + MS MARCO MiniLM rerank | 0.7717 | 0.6340 | 0.6684 |

Recall@5 **−0.0583**. Worst type drop: `scenario` −0.1345. Domain mismatch; did not fine-tune a legal cross-encoder after this.

### 6c. Hard negatives

`results/step4_hard_negative_report.md`, `results/step4_mining_stats.json`. Same-chapter + e8 near-misses, cap 3. Coverage: 5083/5083 examples, mean 2.980 negatives after cap.

| Config | Val Recall@5 | Val MRR | Val NDCG@5 |
|---|---:|---:|---:|
| original-e8 | 0.8299 | 0.6390 | **0.6871** |
| hardneg-e3 | 0.7953 | 0.6003 | 0.6493 |
| hardneg-e8 | 0.7969 | 0.6044 | 0.6528 |

Hardneg-e8 was the better hardneg run and still **0.0343 NDCG below e8**. Winner remained original-e8; test reused (Recall@5 0.8412).

### 6d. Combined GSMS-B + GovIntel training (on GSMS-B val)

Covered in more detail in §7. On the **same val** used to select e8, the best combined config (e5) is still below e8. That is a failed *improvement of the GSMS-B-selected model*, not a claim that GovIntel data is useless (see §12).

---

## 7. GovIntel Extraction & Combined Training

**v1 extraction** (`results/govintel_contamination_check.json`): **846** pairs. Against 12,859 train records that is **6.6%** yield. Regex was too tight for how GovIntel writes citations.

**v2 extraction** (`results/govintel_extraction_v2_report.json`): Patterns A/B/C (section lists + act-first + Applicable statute/section). Zero-hit 7046, multi-hit 1736, extracted **4038**, yield **31.4%**. Contamination vs nyaya-eval-v0: **0** Jaccard>0.5 overlap pairs (same file, `contamination_overlaps: 0`). v1 vs nyaya was also 0 overlaps.

**Combined training** (`results/combined_training_report.md`): 5083 GSMS-B + 4038 GovIntel = **9121** pairs. Fresh bge-small, epochs 3/5/8. Val n=635:

| Config | Recall@5 | MRR | NDCG@5 |
|---|---:|---:|---:|
| original-e8 | 0.8299 | 0.6390 | **0.6871** |
| combined-e3 | 0.7937 | 0.5913 | 0.6423 |
| combined-e5 | 0.8016 | 0.6130 | 0.6605 |
| combined-e8 | 0.8000 | 0.6053 | 0.6544 |

Best combined = **e5**, still **−0.0266 NDCG** and **−0.0283 Recall@5** vs e8 on GSMS-B val. Combined-e5 is kept as a second checkpoint, not as the selected model. Test not re-run.

---

## 8. External Validation (nyaya-eval-v0)

`results/nyaya_eval_external_validation.json`. Independent citizen-phrased set; never used in train or selection.

Filter: 185 BNS/BNSS/BSA rows → gold via citation regex on `expected_answer`/`required_facts` → **85** with a single mapped `chunk_id` (98 no citation, 2 multi, 0 unmapped).

| | n | Recall@5 | MRR | NDCG@5 | Cascade trigger |
|---|---:|---:|---:|---:|---:|
| original-e8 | 85 | 0.6588 | 0.5014 | 0.5410 | 0.0588 |
| combined-e5 | 85 | **0.6824** | **0.5292** | **0.5679** | 0.0588 |

combined-e5 is directionally ahead (+0.0235 Recall@5). n=85 is small. Trigger rate **5.9%** — this is almost pure dense retrieval, unlike GSMS-B val (~22% trigger). Both scores are well below GSMS-B val/test, as expected for questions that rarely name a section.

---

## 9. Stage 1 — Date Extraction

Decision: **no LLM for dates**. Rule-based extract + deterministic 1 July 2024 cutoff (IPC if date < cutoff, else BNS). `CLARIFY` if no usable date.

**Clean GovIntel sample** (`results/stage1_real_eval.json`): n=30, found nothing 0, exact date match **100%**, routing **100%**. Ground-truth dates were parsed from the same extractor on `date_mentioned_in_question`, so this is a consistency check on first-match-friendly text, not an independent labeled NER set.

**Adversarial stress.** The *first* stress run (relative dates, missing dates, offense date not first, cutoff ±1 day, `15/03/24`, `07-01-2024`) is **not preserved as a separate JSON**. The working count from that run was **9/13** scoreable (four first-match multi-date failures; `07-01-2024` left as manual review because dateutil silently picked US order). `results/stage1_stress_test.json` was later overwritten by the v2 extractor and now reads **n_scoreable 14, n_correct 14, accuracy 1.0**.

**v2 extractor** (`results/stage1_v2_eval.json`): keyword context scoring for multi-date (offense vs procedural, window 45); reject ambiguous numeric dates (both parts ≤ 12 and unequal); on score ties, fall back to the first date in the string (needed so GovIntel questions that also mention 1 July 2024 do not CLARIFY). Real GovIntel 30/30 still **100%**. Stress **14/14**, including `ambiguous_numeric_format` on `07-01-2024` → `CLARIFY`.

---

## 10. Legal Action Extraction Decision

Question: should Stage 3 search a short keyword phrase (`"theft"`, `"cheating"`) instead of the raw question?

`results/legal_action_extraction_comparison.json` — original-e8, 300 GovIntel v2 questions, seed 42, zero-shot for e8:

| Query | Keyword hits | Recall@5 | MRR |
|---|---:|---:|---:|
| Raw full question | 0 | **0.910** | **0.703** |
| Keyword phrase | 213 / 300 | 0.260 | 0.167 |

**Confound check** (`results/legal_action_confound_check.json`), same 300, split by `section`/`sec`/`§` + number:

| Subset | n | Raw R@5 | Keyword R@5 |
|---|---:|---:|---:|
| With section number | 175 | 0.937 | 0.177 |
| Without section number | 125 | **0.872** | 0.376 |

Cascade exact-match inflates the headline gap, but raw text still wins by **+0.50 Recall@5** when no section number is present. Keyword collapse is worse *with* citations because it throws away the number cascade would have used.

**Decision:** do not add a separate action-extraction stage. Stage 1 extracts **dates** for routing. Stage 3 gets the **unmodified question**.

---

## 11. End-to-End Pipeline & Act-Aware Cascade Fix

IPC corpus from `mapping.jsonl` → `data/clean/ipc_statutes.jsonl` (**562** sections). e2e cases from GovIntel train.jsonl with Stage 1 date + single gold citation: **460** rows (IPC 355, BNS 105) in `data/clean/e2e_test_cases.json`. Routing gold is Stage 1’s own date, so Stage 2 accuracy is **100% by construction** on this set (`n_clarify` 0). Stage 3 is the real test. Queries are raw text. e8 is out-of-domain on IPC statute text.

**v1 cascade** (`results/end_to_end_pipeline_eval.json`): any section-like number short-circuits, act-agnostic.

| | n | E2E (route ∧ R@5) |
|---|---:|---:|
| Overall | 460 | 78.5% (0.7848) |
| IPC | 355 | 82.0% (0.8197) |
| BNS | 105 | 66.7% (0.6667) |

BNS lagged because temporal questions name **IPC 201 or BNS 238**; cascade stuffed `BNS_201` (wrong act, same number) into the top-5.

**v2 act-aware cascade** (`results/end_to_end_pipeline_eval_v2.json`): exact-match only if the query ties the number to an act that belongs in the corpus being searched (IPC vs BNS/BNSS/BSA), and only the matching chunk prefix.

| | n | E2E |
|---|---:|---:|
| Overall | 460 | **79.1%** (0.7913) |
| IPC | 355 | **82.5%** (0.8254) |
| BNS | 105 | **67.6%** (0.6762) |

Net +3 hits (361/460 → 364/460). Row-level comparison of the two JSON `results` arrays: 3 gains, 0 losses, 457 unchanged. The remaining BNS gap is mostly dense retrieval, not the collision bug.

---

## 12. Model Specialization (e8 vs combined-e5)

Same 460 cases, same act-aware cascade, only the encoder changed.

**Uncontrolled** (`results/end_to_end_pipeline_combined_e5.json`): combined-e5 overall **88.7%**, IPC 87.0%, BNS **94.3%** vs e8 v2 79.1 / 82.5 / 67.6. That BNS jump looked decisive and was not.

**Contamination** (`results/contamination_corrected_comparison.json`): e2e questions vs `govintel_extracted_v2.jsonl` (combined-e5 train). Exact question overlap **151 / 460 (32.8%)**. Leaked combined-e5 acc **91.4%**. Clean **309**: combined-e5 **87.4%**, e8 **82.5%**. Clean IPC n=302: 87.7% vs 83.8%. Clean BNS n=**7**: 71.4% vs 28.6% — unusable. The contamination JSON does not store a BNS leak count; it follows from e2e `n_bns` 105 minus 7 remaining clean BNS (**98 / 105** leaked).

**Style check on 302 clean IPC** (`results/ipc_style_generalization_check.json`): combined-e5 **87.7%** (265/302), e8 **83.8%** (253/302). Disagreements: **18** (15 combined-only, 3 e8-only). These are still GovIntel temporal prompts, just not the exact training strings. There is **no GSMS-B-style IPC slice** in the e2e file, so this does not show combined-e5 winning on GSMS-B writing.

**Unified held-out comparison** (`results/final_unified_model_comparison.json`): act-aware Recall@5, n=**944** = 635 GSMS-B val + 309 clean GovIntel.

| | n | original-e8 | combined-e5 |
|---|---:|---:|---:|
| Overall | 944 | **82.8%** (0.8284) | 82.5% (0.8252) |
| GSMS-B val | 635 | **83.0%** (0.8299) | 80.2% (0.8016) |
| Clean GovIntel | 309 | 82.5% (0.8252) | **87.4%** (0.8738) |
| ↳ GovIntel IPC | 302 | 83.8% | **87.7%** |
| ↳ GovIntel BNS | 7 | 28.6% | 71.4% |

GSMS-B val for e8 matches the original selection Recall@5 **0.8299**. Averaging the two sources makes the models look tied and hides the split: **e8 on GSMS-B-style new-code questions, combined-e5 on GovIntel-style IPC questions.**

**Decision:** original-e8 remains the **reported / selected** model (val-then-single-test on GSMS-B; test Recall@5 0.8412). Specialization is a Discussion finding, not a reason to swap the locked checkpoint. Do not quote a single “overall” 82.8% vs 82.5% as the result.

---

## 13. What’s Still Open

- **Stage 4 (constrained IRAC generation)** — generation working locally (Ollama + Qwen2.5-3B-Instruct on gold chunks); faithfulness verification extensively tested across seven verifier configurations (see §16). Remaining work: wire the chosen soft-flag verifier into the product UI, not re-prove the core generation or eval design.
- **Frontend Prompts 1 and 2** were written in the project plan; this repo has no run logs or outputs confirming they were executed.
- Clean GovIntel **BNS** remains n=7 after decontamination; do not use it for model claims.
- A legal-domain **cross-encoder fine-tune** was suggested after the MS MARCO rerank failed and was not done.
- `results/cleaning_report.json` was never written; use the two specific cleaning JSONs.
- Stage 1’s first stress-test JSON (9/13) was overwritten; only the v2 14/14 file remains on disk.

---

## 14. Comparison Against GovIntel's Prior Work

This section is a third-party check of GovIntel's published Hugging Face README (`aashnasharma/govintel-legal-dataset`) against what this sprint actually opened and measured. It is not a reproduction of their 50-question LLM benchmark.

### Where our findings align with theirs

GovIntel's own 50-question benchmark reports **Temporal Routing** scores of **8.91–9.77** (their scale) even after fine-tuning Llama 3.3 70B Instruct on 12,859 pairs:

| Model | Temporal Routing |
|---|---:|
| Llama 3.3 70B Base | 8.91 |
| GPT OSS 120B | 9.23 |
| Kimi K2.5 | 9.36 |
| GovIntel fine-tuned Llama 3.3 70B | **9.77** |

Temporal routing stayed imperfect for them at 70B. Our Stage 2 gateway is a **deterministic date comparison** against the 1 July 2024 cutoff, not a trained behavior. On the 460-row e2e set, routing accuracy is **100% by construction** (`true_route` is Stage 1's own date; `n_clarify` 0). That is independent evidence for this project's central architectural claim: **Article 20(1) routing should be a hard rule, not something a model is asked to learn**, even when the model is well-resourced.

Caveat already on record: 100% here is not a human-labeled routing eval. It shows the gateway does not invent a second date policy. Their 8.91–9.77 numbers are a different protocol (LLM answers, n=50). The alignment is architectural, not a head-to-head score.

### Where we found their dataset overstates itself

The README Edges table lists **two** mapping-related counts in the same block:

| README row | Published count |
|---|---:|
| Semantic / Deterministic → `IPC_TEMPORAL_PAIR` | **512** |
| “IPC to BNS Mappings” (temporal successor links) | **619** |

Direct inspection (`src/inspect_govintel_ipc_temporal.py`) of `graph/deterministic_edges.json` and `graph/all_edges.json` found **512** `IPC_TEMPORAL_PAIR` edges, **identical** across those files. No 619-edge mapping file was found in that pass. The published **619** does not match the mapping artifact we actually opened. (512 itself is from that inspection run, not a `results/*.json`.)

Those 512 edges carry **no descriptive content**. Example shape:

```
{"source": "BNS_2023_SEC_001", "target": "IPC_1",
 "edge_type": "IPC_TEMPORAL_PAIR", "direction": "source_to_target",
 "deterministic": true, "transition_date": "2024-07-01"}
```

ID schemes also mismatch the section files (`IPC_1` vs `IPC_1860_SEC_1`), so reconstructing a usable table needs a manual join and ID rewrite. Our `mapping.jsonl` is a single standalone table: full IPC/BNS headings and descriptions per row, plus `section` / `partial` / `merged` / `dropped` (294 / 122 / 117 / 29) which their edges do not encode. **The mapping-dataset novelty claim survives direct inspection of their equivalent artifact.**

(The README's **14,280** total training pairs is consistent with 12,859 train + 1,421 eval. This repo processed the **12,859** train split.)

### Where we used their data and it helped

4,038 question–section pairs were extracted from `data/train.jsonl` (**31.4%** yield after the v2 citation-regex fix; v1 was 846 / 6.6%). Combined training (5,083 GSMS-B + 4,038 GovIntel = 9,121) **did not** beat original-e8 on the primary GSMS-B val benchmark (combined-e5 NDCG@5 0.6605 vs e8 0.6871).

On GovIntel-style temporal-transition questions, after exact-duplicate decontamination, combined-e5 **did** beat e8:

| Set | n | original-e8 | combined-e5 |
|---|---:|---:|---:|
| Clean GovIntel (held-out, non-memorized) | 309 | 82.5% | **87.4%** |
| ↳ Clean GovIntel IPC | 302 | 83.8% | **87.7%** |

That is a genuine, verified benefit from their training text, distinct from their multi-agent / 70B architecture. We used extracted (question, `chunk_id`) pairs to fine-tune a small bi-encoder; we did not adopt their graph, LoRA recipe, or benchmark protocol.

### Where our methodology was more rigorous than what their README documents

Their README reports a **50-question** evaluation with composite scores (Overall, Factual Accuracy, Temporal Routing, Legal Reasoning, Section Match F1, IRAC Quality). It does not document a val-then-single-test split, an exact-duplicate leak check between train and eval, or a by-source breakdown.

This sprint had to catch and correct **our own** contamination error:

| Comparison | n | original-e8 | combined-e5 | Status |
|---|---:|---:|---:|---|
| Uncontrolled e2e (same 460) | 460 | 79.1% | **88.7%** | mostly leak |
| Exact overlap with combined-e5 train | 151 / 460 (**32.8%**) | — | leaked acc 91.4% | discarded |
| Clean held-out | 309 | 82.5% | **87.4%** | kept |

The 88.7% vs 79.1% headline was not a fair model comparison. After filtering, the GovIntel-style gap is real but smaller. That mistake is left on the record as evidence of the protocol: **val-then-test**, **exact-duplicate decontamination before claiming a win**, **no single “overall” average as the result**, and **e8 kept as the selected model** even though combined-e5 wins on GovIntel-style questions. Their README does not show an equivalent correction step.

---

## 15. Multi-Period Routing Extension (Split-Offense Detection)

This session extended Stage 2 from a single IPC/BNS label to a detector that can represent continuing or split offenses that straddle 1 July 2024. It was motivated by the GovIntel eval-split head-to-head (§14 / the six “real or ambiguous” disagreements): several of their own answers are two-period (manufacture then use; concealment treated as continuing), which a one-bit gate cannot encode.

### Full-corpus candidate mine

`results/split_offense_candidate_counts.json`. Scanned GovIntel `train.jsonl` + `eval.jsonl` (**14,280** rows; 12,859 train + 1,421 eval). Two signals, no correctness judged:

| Signal | Count |
|---|---:|
| Combined rows | 14,280 |
| Candidates (either signal) | **532** |
| Continuing-offense language (user or assistant) | 376 |
| 2+ distinct calendar dates in the question | 187 |
| Both signals | 31 |
| Train / eval | 475 / 57 |

`results/split_offense_tier_counts.json` then kept only multi-date questions whose parsed dates actually straddle the cutoff: **161** Tier 1 (145 train / 16 eval). Continuing-language-only (no 2+ dates) was **345**. A seed-42 sample of 25 of those (`results/split_offense_tier2_fp_review.json`) was **22 FP / 3 TP (88% FP)** — BNSS “continuance” headings, old judgments, “investigation ongoing”. That bucket was not read in full.

### Abandoned automated FP filter

This is **not** `results/cross_reference_step1_2_report.md` (that file is the earlier corpus-text-merge that hurt strict Recall@5 0.8299 → 0.8079). The abandoned filter here is `results/split_offense_tier1_filter_counts.json` (`src/filter_split_offense_tier1.py`): hypothetical-rephrasing regex + dual positive offense-context scores on the 161.

| | n |
|---|---:|
| Starting Tier 1 | 161 |
| Dropped hypothetical | 11 |
| Dropped procedural-date-only | 136 |
| Remaining | 14 |

Sanity check against four Batch 1 confirmed genuines: three survived; **Case 2 (forging 10 Jan / using 15 Aug) was dropped** (`filter_too_aggressive: true`). Stemming (`forging`/`using` vs `forged`/`used`) and a nearby `prosecution` vetoed a real split. The filter was **abandoned**. Manual review of all 161 continued; the 14-row leftover was not used as a cleaned set.

### Manual review of all 161

All 161 Tier 1 cases were written to `results/split_review_batch_1.md` … `split_review_batch_9.md` (20 each; batch 9 is case 161) and read in full by the user, with a second-opinion judgment on each batch.

The **161-case tally is the user’s completed review, not a `results/*.json`:**

| Judgment | n |
|---|---:|
| Genuine split (two periods) | 12 |
| Ambiguous / inconsistent | 11 |
| Genuine but single law despite two dates | 90 |
| False positive | 48 |
| Total | 161 |

Yield of real two-period splits: **12 / 161 ≈ 7.5%**. Including ambiguous: (12+11)/161 ≈ **14%**. Cases **77, 109, 116** are two separate acts by the same person, not one continuing offense. Existing single-label routing already handles them per-act; they were **excluded from the detector’s target set**.

### Labeled validation set

`data/clean/split_offense_labeled_validation.json`: **9** `genuine_split` + **6** `ambiguous`, taken from the manually judged cases.

Genuine (9): cases **2, 4, 12, 18, 70, 85, 98, 146, 156** (the 12 genuines minus 77/109/116).

Ambiguous (6): cases **14, 24, 54, 79, 123, 139**. Informational only; no gold “correct” for the detector.

### Detector and validated result

`route_with_split_detection` in `src/stage1_entity_extraction.py`. Single-date `extract_offense_date` is unchanged. Split if two act-dates straddle the cutoff, or continuing-language plus a straddle. Output is two periods (IPC then BNS), not a single label.

`results/split_detector_validated_eval.json` (v1, substring keywords): **8 / 9**. Miss = Case 156 (“did not **use** them until July 5”); `used`/`using` did not match bare `use`, and substring `use` would also hit `house`.

Fix: `keyword_in_context` word-boundary match; `"use"` added to `OFFENSE_KEYWORDS`. `\buse\b` hits “did not use them”, not “house”.

`results/split_detector_v2_eval.json`: **9 / 9** genuine (`accuracy_genuine` 1.0). No regression on the other eight. Ambiguous unchanged: **14 and 79** flagged split; **24, 54, 123, 139** single (`n_ambiguous_flagged_split` 2).

**This is an n=9 functional validation, not a statistically robust accuracy benchmark.** Cite it as a validated prototype with a small, real evidence base — not a large-scale benchmarked feature.

### Architectural significance

Stage 2 can now detect and represent genuinely continuing/split offenses instead of collapsing them to one IPC/BNS bit. That is the limitation seen in the GovIntel head-to-head (eval-split Case 1 / labeled Case 146: concealment on 30 June, discovered 5 July; their assistant argued a continuing BNS charge). The gateway is still a hard date rule; the extension is that some questions have **two** dates that both look like acts.

---

## 16. Stage 4 — Constrained Generation and Faithfulness Verification

Stage 4 generates IRAC-formatted answers from retrieved statute text only (no external legal knowledge). All generation evals here use **gold statute chunks** — the correct `chunk_id` from the test split is fed directly, isolating generation quality from retrieval error.

### Setup and initial smoke test

`results/stage4_sample_irac.json`. Ollama + Qwen2.5-3B-Instruct set up locally (`src/stage4_generate.py`). First **5-case** smoke test on gold chunks from `data/splits/test.jsonl`:

| chunk_id | Outcome |
|---|---|
| BNSS_197, BNSS_66, BNS_159, BNSS_450 | Fully correct and grounded |
| BNSS_364 | Distinct failure mode |

**4 / 5** cases fully correct. Case 5 (BNSS 364) revealed a failure that is **not** grounding/hallucination: the model correctly quoted the limiting clause (“after hearing the evidence for the prosecution and the accused”), then produced a Conclusion that ignored it — an internal Rule/Application/Conclusion inconsistency, not fabricated content.

### Larger validation sample

`results/stage4_larger_sample.json` and `results/stage4_review.md`. **40** gold-chunk cases: **20** `exceptions` (oversampled — where the Case 5 pattern appeared) + **20** general mix (seed 42). Manually reviewed by the user:

| Judgment | n |
|---|---:|
| Grounded & consistent | 31 |
| Grounded but Rule/Conclusion mismatch (cases 6, 9, 12, 13, 39) | 5 |
| Other / imprecise issues | 4 |
| Fabricated content | **0** |

**Zero hallucination across all 40** is a strong result on the core safety property. The **5 / 40 (12.5%)** logical-consistency failure rate is the real finding requiring mitigation.

### Verifier design iteration (seven configurations tested)

Each configuration scored against the same **5** known mismatches (cases 6, 9, 12, 13, 39) and **35** other cases treated as consistent for the mismatch detector.

**1. Rule + Application + Conclusion, 3B** (`results/stage4_verifier_eval.json`)

| TP | FP | FN | TN | Precision | Recall |
|---:|---:|---:|---:|---:|---:|
| 2/5 | 4 | 3 | 31 | 0.333 | 0.400 |

Caught only the two most overt self-contradictions (cases **6**, **39**). Missed the three “coherent but wrong” cases (**9**, **12**, **13**) where Application and Conclusion agree with each other but not the statute.

**2. Rule + Application + Conclusion, 14B** (`results/stage4_verifier_ablation.json`, `model_14b`)

| TP | FP | FN | TN | Precision | Recall |
|---:|---:|---:|---:|---:|---:|
| 2/5 | 2 | 3 | 33 | 0.500 | 0.400 |

Recall identical to 3B — bigger model improved precision only (FP 4 → 2), never recall.

**3. Rule-only (Application hidden), 3B** (`results/stage4_verifier_ruleonly.json`)

| TP | FP | FN | TN | Precision | Recall |
|---:|---:|---:|---:|---:|---:|
| 5/5 | 32 | 0 | 3 | 0.135 | 1.000 |

Confirmed the **anchoring hypothesis**: showing the verifier its own flawed Application trace caused it to rubber-stamp coherent-but-wrong chains. Hiding Application raised recall from 40% to 100% at the cost of a **91% false-positive rate** (32 / 35 consistent cases flagged).

**4. AND gate: 3B Rule-only + 3B Rule+App+Conc** (`results/stage4_verifier_combined.json`)

| TP | FP | FN | TN | Precision | Recall |
|---:|---:|---:|---:|---:|---:|
| 2/5 | 4 | 3 | 31 | 0.333 | 0.400 |

Mathematically **identical** to 3B Rule+App+Conc alone — that MISMATCH set was a strict subset of the Rule-only NOT_SUPPORTED set.

**5. Rule-only, 14B** (`results/stage4_verifier_ruleonly_14b.json`)

| TP | FP | FN | TN | Precision | Recall |
|---:|---:|---:|---:|---:|---:|
| 5/5 | 20 | 0 | 15 | 0.200 | 1.000 |

Same full recall as 3B Rule-only; **12 fewer** false positives (32 → 20).

**6. AND gate: 14B Rule-only + 3B Rule+App+Conc** (`results/stage4_verifier_14b_and_3b.json`)

| TP | FP | FN | TN | Precision | Recall |
|---:|---:|---:|---:|---:|---:|
| 2/5 | 2 | 3 | 33 | 0.500 | 0.400 |

Best precision among AND-gate variants (FP 4 → 2), but recall **capped at 40%** by the smaller Rule+App+Conc input set — a hard ceiling, not solvable by further AND tuning.

**7. Rule-only, Claude Sonnet 4.5** (`results/stage4_verifier_claude.json`)

| TP | FP | FN | TN | Precision | Recall |
|---:|---:|---:|---:|---:|---:|
| 5/5 | 13 | 0 | 22 | 0.278 | 1.000 |

Full recall maintained. Precision continued improving with model scale on the Rule-only design: **3B 0.135 → 14B 0.200 → Claude 0.278** — consistent upward trend, no plateau reached at these scales.

**Infrastructure note:** Claude runs required real API setup (Anthropic key creation, `ANTHROPIC_API_KEY` in the environment). An environment-propagation issue was encountered: Cursor’s agent shell initially did not inherit the same working key as the user’s own terminal (401 authentication errors until the key was confirmed in the agent environment). This is a real deployment footgun, not a hypothetical one.

### Key findings

- **Rule-only is the structural fix for recall.** Hiding Application from the verifier enables full recall (5/5) across all three model scales tested (3B, 14B, Claude). No Rule+App+Conc configuration exceeded 2/5 recall.
- **Precision scales with model capability on Rule-only.** 13.5% → 20.0% → 27.8% (3B → 14B → Claude). The ceiling for a fully automated hard-block gate has not been reached at these scales, but **none tested is precise enough to deploy as a silent auto-reject** — even Claude would incorrectly flag roughly **3 good answers for every 1 real problem** caught (13 FP / 5 TP).
- **AND gates cannot beat the Rule+App+Conc recall ceiling.** Best AND result: 2/5 recall, 0.500 precision — useful for trimming FPs, useless for catching cases 9, 12, 13.
- **Final design decision:** Verification uses a capable model (**Claude**, via API) as a **“needs review” soft flag** shown to the user alongside the raw retrieved Rule text — **never a silent hard block**. Generation remains **local** (Qwen2.5-3B via Ollama) per the project’s cost/latency architecture; only the infrequent, short verification call uses the API. This split is intentional and does not conflict with the local-generation design rationale.

---

## 17. Verification Prompt Refinement — Citation-Label Fix

`results/stage4_verifier_14b_v3_citation_fix.json`. While testing the live backend on a real query ("If the riot occurred on August 10, 2024, which law would govern the agent's liability?"), the 14B v2 verifier produced a false positive (`NOT_SUPPORTED`): the generated Conclusion mentioned "Section 193 of BNS 2023", but the retrieved statutory Rule snippet did not contain its own section header. The verifier flagged this as unsupported external text even though the substantive legal conclusion (an agent's liability for failing to disperse a riot on behalf of a landowner) was fully supported by the Rule snippet.

To address this pattern, the verification prompt in `src/stage4_verify_ruleonly_14b_v2.py` (and wrapped by `app/stage4.py`) was refined with:
1. **An explicit criterion:** Do NOT flag `NOT_SUPPORTED` because the Conclusion mentions a section number, act name, or citation label absent from the Rule text. Judge only the substantive legal claims against the Rule text.
2. **A fourth few-shot example:** A dedicated example demonstrating the BNS 193 riot liability case marked as `SUPPORTED`.

### Evaluation on Full 40-Case Labeled Set

The prompt refinement was tested against the full 40-case labeled benchmark (`results/stage4_larger_sample.json`, 5 known mismatches):

| Configuration | TP | FP | FN | TN | Precision | Recall |
|---|---:|---:|---:|---:|---:|---:|
| 14B v2 (prior few-shot) | 5/5 | 12 | 0 | 23 | 0.294 | 1.000 |
| **14B v3 (citation-fix)** | **5/5** | **10** | **0** | **25** | **0.333** | **1.000** |

### Key Findings
- **Generalization beyond the design case:** In addition to fixing the riot-liability query, the new prompt resolved a second false positive on the gold benchmark — **Case 35 (BNS_341 counterfeit seals)**, which previously failed because the Conclusion referenced Section 341 while the Rule text mentioned Section 338.
- **Zero regression on recall or new errors:** All 5 true mismatches (Cases 6, 9, 12, 13, 39) remained caught (Recall = 1.000), and 0 new false positives were introduced across the other 35 cases.
- **Remaining false positives:** The remaining 10 false positives (`[1, 2, 3, 4, 16, 18, 20, 22, 32, 38]`) belong to different error categories (e.g. over-strict interpretation of negative inferences, or procedural consequences not affirmatively written in the snippet). Further prompt tuning on these was deliberately deferred as diminishing returns, given that 100% recall with ~33.3% precision is well-suited for a non-blocking "needs review" flag architecture.

---

## 18. Backend Integration — FastAPI Service and Bifurcation Handling

The individual components developed and evaluated across Stages 1–4 were assembled into an end-to-end FastAPI application (`app/main.py`) running locally with Uvicorn.

### Pipeline Architecture & Endpoints
- **Stage 1:** Rule-based date extraction (`app/stage1.py`, wrapping `src/stage1_entity_extraction.py`) with per-thread conversation locking (`conversation_id`).
- **Stage 2:** Deterministic date gate (`app/stage2.py`) routing `< 2024-07-01` to IPC and `>= 2024-07-01` to BNS.
- **Stage 3:** Act-aware cascade retrieval (`app/stage3.py`, using `models/finetuned-bge-small-ipc-bns-e8` over `data/clean/ipc_statutes.jsonl` and `data/clean/statutes.jsonl`).
- **Stage 4:** Constrained IRAC generation via local Ollama `qwen2.5:3b-instruct` and soft verification via local Ollama `qwen2.5:14b-instruct`.
- **Response Schemas:** Fully typed via Pydantic (`app/schemas.py`) matching the frontend's expected discriminated union: `MappingResponse`, `ClarifyResponse`, `BifurcationResponse`, and `FailureResponse`.

### Bifurcation Handling & Score-Gap Heuristic
In Stage 3, when dense retrieval scores indicate that multiple distinct sections are close in relevance, silently taking the top-ranked result can discard a legally valid alternative. A score-gap heuristic was added in `app/stage3.py`:
- `detect_bifurcation(retrieved_with_scores, margin=0.10)` checks whether candidates within the top-4 are within 10% of the top cosine similarity score.
- When multiple candidates meet this threshold, `POST /api/query` returns a `BifurcationResponse` containing section options and one-sentence statutory descriptions.
- A dedicated continuation endpoint, `POST /api/query/resolve_bifurcation`, allows the user to select one section. It bypasses Stage 3 retrieval re-execution and proceeds directly to Stage 4 IRAC synthesis and verification on the selected chunk.

### Test Validation & Regression Checks
The backend was validated end-to-end against an 8-query test suite:
1. **Regression on original 5 smoke queries:**
   - Single-answer queries (Obscene magazines → IPC 292; Evidence destruction → IPC 201; Riot agent liability → BNS 193) produced standard `mapping` responses with no false bifurcation triggers (score gaps > 14%).
   - Missing date query produced `clarify` as expected.
   - The query *"A person is caught selling counterfeit banknotes to an undercover officer on September 5, 2024"* surfaced a genuine bifurcation between BNS 178, 179, and 180 (gap < 0.1%). Inspecting the full statutory text verified that these are distinct legal offenses (manufacturing vs trafficking/using vs possession with intent), proving the score-gap heuristic correctly surfaced real statutory ambiguity rather than noise.
2. **Real bifurcation probes from Stage 3 validation near-misses:**
   - Death-sentence tie-breaking rule correctly offered `BNSS 411`, `BNSS 433`, and `BNSS 410`.
   - Trafficking exploitation correctly offered `BNS 144` and `BNS 143`.
   - Organised crime definitions correctly offered `BNS 111` and `BNS 112`.
3. **Resolve flow:** Calling `/api/query/resolve_bifurcation` with `BNSS 433` successfully returned a full `mapping` response with pipeline provenance noting user resolution.

### Open Work
- **Frontend Integration:** The UI remains connected to mock data and has not yet been connected to the live FastAPI backend.
- **Translation Layer:** The planned multilingual translation pipeline (IndicTrans2) has not yet been integrated or tested.

---

## 19. Frontend Language Toggle & Multilingual Fix

Static page copy and live IRAC translation are separate systems. Landing-page strings (nav, hero, FAQ, chat chrome) are served from an `i18n.ts` dictionary keyed by `en` / `hi` / `mr`. Live IRAC bodies are translated only after Stages 1–4 finish, in Stage 5 (`app/stage5_translate.py`), so language choice never changes routing, retrieval, or verification.

Early live HI/MR chat answers looked fluent but were wrong in substance: dates drifted (e.g. 5 September → 9 August), subjects flipped ("a person" → "an animal"), and fabricated detail appeared. That path was temporarily short-circuited for both `hi` and `mr` after confirming the failure was not Stage 5 latency but bad translation content.

Root cause: Hugging Face access to `ai4bharat/indictrans2-en-indic-1B` returned **403** (gated model). The pipeline fell back to Ollama translation without making that failure obvious in the product response. IndicTrans2 never ran; Ollama did. An earlier teammate-approved Hindi review was later traced to the **same Ollama fallback**, not IndicTrans2 — so that approval could not stand as evidence that the intended engine worked. Re-validation after fixing access was required, not optional.

Fix: request and receive HF model access, set `HUGGINGFACE_HUB_TOKEN` in the FastAPI process environment, pin a transformers/tokenizer stack that loads IndicTrans2, and disable silent Ollama fallback for HI/MR once IndicTrans2 is available. Batch Stage 5 translation was also added so all IRAC fields share one forward pass.

Re-check on the live `/api/query` path: **6/6** cases (counterfeit / riot / magazines × `hi` + `mr`) returned `engine=indictrans2` with date and subject preserved — no Ollama drift pattern. Stage 5 itself is a few seconds when batched; remaining end-to-end latency was dominated by Stage 4 until the Ollama Metal fix (§20).

---

## 20. Ollama Performance Root Cause — Rosetta/x86 Binary

Isolated Stage 4 EN timings (no translation) on the three chat smoke queries were **~102–148s** total per request. Sub-step profiling showed almost all of that in the two Ollama calls (`generate_irac` on `qwen2.5:3b-instruct`, `verify_rule_only_14b_v2` on `qwen2.5:14b-instruct`); extract / gate / retrieve / parse were negligible.

Root cause: the active binary was Homebrew’s **Intel x86_64** build under `/usr/local/Cellar/ollama/0.9.6`, running via Rosetta on Apple M4 Pro (arm64, 48 GB). Server startup logged `inference compute … library=cpu` with empty Metal fields; `ollama ps` showed **100% CPU**; ggml reported SSE3/SSSE3; eval rate was ~**11 tok/s**. `OLLAMA_LLM_LIBRARY` was unset — CPU was selected because no GPU library was available to a Rosetta process, not because of an explicit env force. Version was also stale (**0.9.6** vs current **0.34.x**), but architecture was the blocking issue.

Fix: stop `ollama serve`, `brew uninstall` the Intel Cellar package, install via `arch -arm64 /opt/homebrew/bin/brew install ollama` (**0.34.4** arm64). Fresh serve logged `library=Metal` / Apple M4 Pro; `ollama ps` showed **100% GPU**; CLI eval rate ~**96 tok/s**. Stage 4 EN totals after the swap: **~6–23s** (about **5.6×–24×** vs the Rosetta baseline, case-dependent).

The riot case’s first-after-Metal **~20.9s** `generate_irac` was checked separately: `ollama` logs showed eviction when loading 14B at `num_ctx=32768` under `system_limited=true`, then a cold 3B reload on the next generate. Dual back-to-back runs with both models already resident kept riot generate at ~**2.9s** every time — not content-specific. A FastAPI startup warm-up (trivial 3B generate + 14B verify after Ollama health check and Stage 3 corpus load) pays the co-residency cost once at boot (**~11.4s** in the measured restart); the first real Stage 4 request after Ready was **~5–6s**, matching steady state rather than the cold-swap spike.

---

## 21. Landing Page & Chat Interface — Built and Verified End-to-End

The LawShift frontend is a **Next.js + TypeScript** App Router app under `frontend/` (chosen over Vite and static HTML for App Router layout and a straightforward FastAPI proxy/integration path). Visual brief deliberately avoided generic AI-template defaults: **Source Serif 4 + Manrope**, Professional Dark / Minimal Light themes, a client-side date-gate widget that mirrors Stage 2’s deterministic cutoff, a trust strip (**100%** routing / **0.841** Recall@5 / **0** fabricated citations) taken from real evaluation artifacts, and a comparison table aligned with the paper’s Table 1 framing.

The chat workspace is **embedded on the landing page** (`ChatEntry`), not a separate route. Language toggles EN/HI/MR for both static copy and the `language` field on `/api/query`.

API-only testing missed frontend bugs that only showed up in the browser:

1. **Stale Next.js client chunk.** The tab was still loading an old bundle (`_c319c3e6._.js`) that inlined bifurcation as non-clickable bullet text (no `resolve_bifurcation`) and truncated mapping display to roughly `Mapped` + `(conclusion || issue)`. On-disk `ChatEntry.tsx` already had buttons and full IRAC fields, but the long-running `next dev` process had not picked them up. Fix: kill `next dev`, `rm -rf .next`, restart; browser then loaded `src_components_a49c5ef0._.js` with `bifurcationOptions` buttons, `resolve_bifurcation`, and Issue/Rule/Application/Conclusion rendering.

2. **Sources and verification never rendered.** Every `mapping` response already included `sources` and `verification`; the client discarded both. Fix: store them on the message object; render **Sources (N)** after Conclusion with statute text collapsed by default; show verification on **every** mapping — quiet checkmark + note when `flagged=false`, amber “Worth double-checking” + `confidence_note` when `flagged=true`.

Live browser checks (real network calls, not forced verifier payloads): counterfeit → bifurcation buttons → **BNS 180** resolve returned full IRAC + Sources + quiet verify; expand/collapse of statute text worked. For the amber path, **case 6** from `results/stage4_larger_sample.json` (euthanasia / BNS 26, one of the five labeled Rule/Conclusion mismatches) was run through the UI with a dated prefix for Stage 1; after selecting **BNS 26**, `resolve_bifurcation` returned real `flagged=true` and the amber card showed the genuine `NOT_SUPPORTED` confidence note. Re-probing all five original mismatch cases (6, 9, 12, 13, 39) on the live generate+verify path found only **2/5** re-flagged (6 and 13 on that run). That is expected for a stochastic generator whose live IRAC text is not the frozen sample the verifier was scored on; the **100% recall** figure remains a property of that fixed labeled evaluation set, not a guarantee that every live re-generation of those questions will flag again.

---

## 22. Missing-facts gate (date with no facts)

### Failure

After Stage 1 locked a date, fact-free follow-ups still went to Stage 3. Measured diagnosis (real `handle_query`, nothing stubbed):

| Query | Status | Top-1 score |
|---|---|---:|
| "Which section is this case for" then "25/6/24" | mapped | 0.297 |
| "25 June 2024" | bifurcation | 0.227 |
| "Which law applies to this? 10 August 2024" | bifurcation | 0.317 |
| "Tell me the section. 5 September 2024" | bifurcation | 0.278 |
| "Is this legal? 12 March 2024" | bifurcation | 0.297 |
| "Help. 1 July 2024" | mapped | 0.346 |

Controls with real facts stayed higher (top-1 ≥ 0.469). There was no clarify that asked for facts once a date was known — only date clarify, then a confident wrong map or bifurcation on unrelated sections.

`detect_bifurcation` (called from `handle_query` after sorting cascade scores) keeps a neighbour when `score >= top_score * (1 - margin)` with default `margin=0.10` (within 10% of top, checking the next three scores). That is a relative gap, not a quality floor, so low-scoring fact-free queries still bifurcated.

### Fix

In `handle_query`, after Stage 2 routes and **before** Stage 3 retrieval: strip the Stage 1 matched date text (re-extract a date span from the current message when the date is conversation-locked), lowercase, strip punctuation, drop stopwords and `MISSING_FACTS_META_WORDS`, drop pure digits. If zero content tokens remain, return `ClarifyResponse` with `reason="missing_facts"` and the message asking the user to describe what happened. Date stays locked. One leftover content word lets the query through.

Frontend: same clarify path as date clarify (EN uses `data.question`; HI/MR use `clarifyFallbackFacts`). Free-question limit: `ChatEntry` decrements remaining after every `/api/query` response including clarify — date clarify already counted; missing_facts counts the same way.

Upload: short extracts (&lt;20 chars) that Stage 1 can still parse as a date now reach `handle_query` so date-only documents return `missing_facts` instead of `source_unavailable`.

No retrieval-score threshold was added.

### Test results

- **4a** Nine diagnosis queries: 1–6 → `clarify` / `missing_facts` (no retrieval). 7–9 → same status and top-5 as the diagnosis (bifurcation / mapped / mapped; scores unchanged to 1e-6).
- **4b** After missing_facts on "25 June 2024", "a man sold obscene magazines" used locked `2024-06-25`, did not ask for the date again, returned bifurcation with IPC 292 top-1.
- **4c** ~30 fact-free variants: 27 blocked. **3 not blocked** only because Stage 1 does not parse ISO `2024-07-01` (no date → missing_facts never runs); not a gate miss on dated text.
- **4d** False-block: **0** on the 185 nyaya-eval filtered questions and a random 200 of the 636 test questions (each with `25 June 2024` appended). The published “85” set is the single-citation subset of those 185; all 185 passed, so the 85 do too. No list change.
- **5** Top-1 score distribution (no threshold applied): fact-free n=30 min **0.162** / p10 **0.224** / median **0.318**; real+date n=385 min **−0.165** / p10 **0.205** / median **0.347**. The bands overlap — a score floor would cut real questions.
- **4f** Date-only document text → `missing_facts`; fact-rich document → mapped (IPC 292).
- **Stage 1** re-run: **44 of 44** (30 real + 14 stress) — same as earlier.
- **Stage 3** re-run (cascade + e8 on `test.jsonl`): Recall@5 **0.8412** (535/636) — same as earlier **0.841**.

---

## 23. IPC↔BNS code mismatch (citation vs offence date)

### Failure

Users sometimes name a section in one code while the offence date routes to the other (for example BNS 103 on 25 June 2024, when IPC still applies). The pipeline could still run retrieval in the wrong corpus, or ignore the named section and return unrelated hits. A bare “section 302 on 5 July 2024” with no IPC/BNS prefix could bifurcate among homonymous BNS/BNSS sections instead of treating an explicit cross-code cite as a mapping problem.

### Rule

After Stage 2 locks the route, if the message contains an explicit **IPC** or **BNS** section citation and that code disagrees with the route, intercept **before** Stage 3: consult the IPC↔BNS mapping table. One or more equivalents → offer those sections in a bifurcation prompt and **do not** run retrieval. No table equivalent (including sections dropped in the new code, e.g. IPC 7) → clarify and ask for facts. **BNSS**, **BSA**, **CrPC**, and bare section numbers without an IPC/BNS prefix are unchanged — normal retrieval and score-gap bifurcation still apply.

### Schema

Reuse `BifurcationResponse` and `ClarifyResponse` with optional `reason="code_mismatch"` so the client can tell mapping offers apart from score-gap bifurcation. Resolution still goes through `resolve_bifurcation`; mapped answers decrement the free-question quota; clarify and bifurcation do not.

### Test results

Harness output in `/tmp/lawshift_mismatch_out.json` (live `handle_query`, Stage 3 loaded):

- **Six** explicit mismatch cases: all `reason=code_mismatch`, empty top-5, `retrieval_ran=false` (BNS 103→IPC 302 on 25 June 2024; IPC 302→BNS 103 on 5 July 2024; Section 302 IPC same date; BNS 294→IPC 292; IPC 124A→BNS 152; IPC 201→BNS 238).
- **IPC 7 on 5 July 2024** → clarify (`code_mismatch`), no mapping equivalent.
- **BNS 1 on 25 June 2024** → bifurcation with IPC mapping options (live run lists IPC 1–3 when the table maps multiple IPC sections).
- **Bare** “section 302 on 5 July 2024” → unchanged score-gap bifurcation (BNS 302 / BNSS 302 / BNSS 304), retrieval ran.
- Matching-code controls (IPC 292 on IPC date, etc.) still map or bifurcate as before; BNSS/CrPC procedure cites unchanged.
- Playwright free-question quota: **5 → 5 → 5 → 4** (initial; after date clarify; after mismatch bifurcation; after resolve to mapped).
- Regressions: Stage 1 **44/44**; Stage 3 Recall@5 **0.8412** (535/636).
- Nyaya **85** set with margin 0.10: **47** retrieval-only bifurcations (same as prior part B); one row that cited IPC 302 on a BNS-routed date now hits the code-mismatch intercept instead of score-gap bif.

Citation extractor: strings like “BNS 2023 reforms and IPC 302” or “section 302 on 5 July 2024” without a code prefix before the section number do not register as explicit IPC/BNS cites (empty extract) — by design for bare-section queries.

---

## 24. Citation-only section lookup, bifurcation escape, and date-lock diagnosis

### Citation-only finding

After the missing-facts gate started letting **explicit citations** through (so “IPC 292 on 25 June 2024” was no longer blocked), those messages still ran Stage 3 retrieval and Stage 4 writing with **no offence facts**. The model then invented an issue line or bifurcated among dense neighbours of the named section. Users who only named a section were treated as if they had described a case.

**Rule (unchanged retrieval / margin / prompts):** after Stage 2 and the existing code-mismatch intercept, if the message is **citation-only** — strip the matched date and every `EXPLICIT_CITATION_RE` span, then apply the same meta/stopword token filter as missing-facts; if nothing content-like remains — and the cited IPC/BNS code **matches** the date’s route, **skip retrieval and writing**. Return a new response kind `section_lookup` with up to three citations: code, section, corpus heading, full statute text as stored, and one mapping line (table type wording, or “No equivalent is recorded in our mapping table”). If the section is absent from the corpus: “`<code> <n> is not in the statute text we hold.`” One fixed note asks the user to describe what happened. Date stays locked; the free-question counter does **not** decrement (only mapped answers count). Code-mismatch behaviour is unchanged. A citation **plus** fact words is unchanged and still maps or bifurcates normally.

**Schema:** smallest addition — `SectionLookupResponse` / `SectionLookupItem` beside the existing AssistantMessage union. Frontend reuses the collapsed **sources** panel pattern in chat and Workspace; HI/MR use fallback strings marked for native review (same pattern as date/mismatch clarify).

**Bifurcation escape:** every bifurcation response (score-gap and code-mismatch) appends a final option “None of these. I will describe what happened”. Choosing it clears pending bifurcation, returns clarify (`reason=describe_facts`) asking the user to describe the facts and search again, keeps the date locked, and does not decrement the counter. Offered sections and the 0.10 margin are unchanged.

### Date-lock diagnosis (read-only, this round)

`_LOCKED_DATES` stores the first resolved offence date for a `conversation_id` and **never updates** when a later message contains a different date. Locked turns set Stage 1’s matched span to `(locked)`; the missing-facts strip re-extracts a date span from the *current* message so leftover digits are not treated as facts. Follow-up dates therefore do not re-route IPC↔BNS for that thread.

Separately: IPC 7 is present in the corpus and in the mapping table (often as a dropped / definitional row). Dense score-gap bifurcation after a fact-rich query does not guarantee IPC 7 appears among the close-score options — that is retrieval neighbourhood behaviour, not a missing-chunk bug. Stage 4’s Issue line remains the single-sentence slot required by the generation prompt.

### Test results

Harness under `/tmp` (live `handle_query`; Stage 1 / retrieval / margin / Stage 4 / verifier / models untouched):

- **1e** Citation-only → `section_lookup` for IPC 292 / 302 / 7, BNS 103 (both phrasings), Section 302 IPC; IPC 99999 → not-in-corpus line; date locked. Control with facts → normal bifurcation (IPC 292 / 293 + escape), not `section_lookup`.
- **2b** Counterfeit case bifurcates BNS 180 / 179 + escape; after “None of these” → `describe_facts` clarify; facts follow-up → normal answer. Obscene example mapped without score-gap bif on this run; the citation+facts control still offered the escape on bif.
- **3** Nine diagnosis: 9/9. Fact-free ~30: 27 blocked / 3 ISO no-date. False-block 285: **0**. Stage 1 **44/44**. Stage 3 Recall@5 **0.8412** (535/636). 85-set bif @0.10: **47**. Six code-mismatch: **6/6**. Stubbed quota: date **5**, section_lookup **5**, bifurcation **5**, choose mapped option **4**.

---

## 25. Locked-date conflict when a later message names a different date

### Failure

Once a conversation locked an offence date, later messages that named a different date were ignored for routing. `_LOCKED_DATES` was reused unconditionally; Stage 1 was not compared with the lock. After “BNS 103 on 25 June 2024” and choosing IPC 302, “IPC 124A on 5 July 2024” stayed on the IPC lock and returned a mapped IPC 124A answer, whereas the same message in a fresh conversation offered BNS 152 via the code-mismatch path.

### Rule

When a lock exists and Stage 1 finds a date in the current message:

- **Same date:** unchanged.
- **Different date, same side of 1 July 2024** (both before, or both on/after): keep the lock for routing; attach `date_lock_label` so the client shows one line — “Using the offence date you gave earlier: {locked date}.” — and do not ask a question.
- **Different date, opposite sides of the cutoff:** do **not** run retrieval. Return `BifurcationResponse` with `reason="date_conflict"`, the two dates as options, and prompt text naming each date’s code. Choosing a date replaces the lock and re-runs the held message under that date (`reason=date_conflict_resolved` so the message’s own date does not re-conflict). A new free-text message abandons the pending conflict and is processed normally (subject to the same check).
- **No lock yet:** unchanged.

Free-question quota: `date_conflict` does not decrement; a mapped answer after resolve counts once (same as other bifurcations).

**Smallest schema change:** extend `BifurcationResponse.reason` with `"date_conflict"`; add optional `date_lock_label` on existing response kinds for the same-side note. Reuse the existing bifurcation resolve endpoint.

Stage 1 is unchanged. Multi-date messages still yield a single extracted date (`multi_date_context_resolved` or `tied_fallback_first_date`); the conflict check compares that one date to the lock.

### Test results

Harness under `/tmp` (`lawshift_date_conflict_verify.py`, `lawshift_date_conflict_part3.py`):

- **a** Lock 25 June → IPC 302; “IPC 124A on 5 July 2024” → `date_conflict`. Choose 5 July → lock 5 July / BNS, `code_mismatch` offering BNS 152. Choose 25 June → lock stays IPC; held message continues under IPC (`section_lookup` for IPC 124A).
- **b** Lock 25 June; same-side “20 June 2024” follow-up → `date_lock_label=25 June 2024`, route IPC.
- **c** Lock BNS date; “30 June 2024” → `date_conflict`.
- **d** Pending `date_conflict` dropped when a new message arrives.
- **e** Fresh conversations: same messages as a–c behave as before the lock (mismatch / map or bif on their own dates).
- **f** Regressions: diagnosis nine pass; fact-free ~30; false-block 285 **0**; Stage 1 **44/44**; Recall@5 **0.841**; 85-set bif **47**; code-mismatch **6/6**; section_lookup **7/7**; stubbed landing counter **5 → 5 → 5 → 5 → 4** (date / section_lookup / date_conflict / choose mapped).

---

## 26. Stage 4 conclusion wording — prompt variant (not adopted)

### Problem

On mapped fact-pattern answers the 3B writer often (a) treated unstated legal elements as proved in Application (e.g. that magazines “are lascivious”), (b) wrote Conclusions with “is guilty” / “should be punished” / “is liable”, and (c) omitted penalty / Exception text from the Rule even though the full section was in context. The 14B verifier only sees Rule + Conclusion, so Rule omissions are invisible to it. Hindi translation can also soften English modals (“shall” → “could”).

### Variant

`src/stage4_generate.py` gained `STAGE4_PROMPT_VERSION` (`v1` default / unset; `v2` experimental). Same IRAC headings and one-sentence Conclusion. v2 instructions: Conclusion only says whether the facts appear to fall within the section; Application must not treat unstated elements as met; mention Exception/Explanation/Proviso if present; Rule must quote penalty where the section has one; no placeholder leaks. The running app was **not** switched; eval called `generate_irac` directly from `/tmp` scripts.

### Comparison (summary in `results/stage4_conclusion_wording.json`)

| Measure | v1 (default) | v2 |
|---|---:|---:|
| Fact-20 Conclusions with guilty/punishment wording | **13** | **0** |
| Fact-20 guilty-phrase hits (full IRAC) | 31 | 20 (mostly `shall be punished` inside Rule quotes) |
| Gold-40 automated fabrication flags | 2 | 3 |
| Gold-40 14B v3 verifier flagged | 17 | **36** |
| Fact-20 14B v3 verifier flagged | 2 | 7 |
| Exception/Explanation/Proviso mentioned when section has them (fact-20) | 0/9 | 0/9 |
| Format defects (empty / multi-sentence Conclusion / unparseable / placeholder) | 0 | 0 |

“0 of 40 fabricated” on the original sample was **hand review**. Automated approximation (quoted Rule spans ⊆ section after whitespace normalisation; section numbers in output match the given chunk or appear in the section) flags **4/40** on the stored file (quote normalisation / truncation false positives), not new hallucinations.

### Decision rule / recommendation

**Keep v1 as default.** Do not adopt v2 yet: Conclusions improve sharply, but verifier flags roughly double on the gold-40 set, automated fabrication ticks up slightly, Exception/Proviso mentions did not improve, and some v2 gold Conclusions cited the wrong act/section (e.g. “IPC 292” on BNSS cases). Revisit after tightening v2’s citation discipline and Exception instructions, with a human read of the ten Application pairs in the summary JSON.

---

## 27. Bifurcation escape loop, cited-section honour, mismatch→card

### Problems

1. Choosing “None of these” and then resending the same facts asked the same score-gap question again.
2. A message that already named an in-force section (e.g. IPC 292 with facts) still asked among close-score neighbours (292 vs 293).
3. After a code-mismatch offer on a citation-only message (e.g. BNS 103 on an IPC date), choosing the mapped section ran the writer on the citation string and could invent a person / leak placeholders.

### Rules (default Stage 4 prompt / verifier / retrieval / margin unchanged)

- **Rejected-set cards:** per `conversation_id`, remember score-gap options dismissed via “None of these”. If a later score-gap set is entirely within that rejected set, do not ask again — return `section_lookup` cards (up to three: code, section, heading, statute text) with note “I could not narrow this down further…”. No IRAC; quota unchanged. Different facts that yield a new section still bifurcate.
- **Cited section + facts:** when the message has offence facts and an explicit IPC/BNS citation of the code Stage 2 selects, and that section exists in the corpus, skip score-gap bifurcation in `handle_query` and answer under the cited chunk. `detect_bifurcation` itself is unchanged. Missing cited section → continue on facts and attach `info_note` (“…is not in the statute text we hold; searching on your facts instead.”). BNSS/BSA/CrPC and code-mismatch paths unchanged.
- **Mismatch resolve on citation-only:** pending code-mismatch state records `held_citation_only`; choosing a mapped option returns a `section_lookup` card for that section instead of calling the writer. Held messages with facts still get a normal mapped answer.

### Localisation

New HI/MR strings (agent drafts, need native review): `sectionLookupExhaustedNote`, `sectionMissingSearchNote`.

### Citation date-digit guard

`extract_ipc_bns_citations` now strips the Stage 1 date span and rejects a code+number pair when the number is the day of a following month name (so “under the BNS 5 July 2024” is not treated as BNS 5). Honour / mismatch paths pass `strip_date`.

### Tests (`/tmp/lawshift_p123_verify.py`, `/tmp/lawshift_p123_part4.py`, `/tmp/lawshift_bif85_recount.py`)

| Check | Result |
|--------|--------|
| Part 1 None-of-these → cards (IPC 292/502; BNS 180/179); new facts → normal map | pass (date locked) |
| Part 2 cited+facts → map cited; missing cite → info_note + search | pass |
| Part 3 citation-only mismatch → section card; facts → mapping | pass |
| Diagnosis 9 | 9/9 |
| Fact-free ~30 | 27 blocked + 3 no_date |
| False-block 285 | **0** blocked |
| Stage 1 | **44/44** |
| Recall@5 | **0.841** |
| Bif85 (was 47) | Honour-driven skips **0** after date-digit guard (earlier “3 skips→44” were BNS+day false cites). Recount **46** with comma-appended date (punctuation artifact vs space-append baseline **47**). |
| Explicit cites → status change | 85-set: **5** cites / **1** change; 200-set: **35** cites / **0** changes |
| Code-mismatch 6 | 6/6 |
| Section lookup 7 | 7/7 |
| Date-conflict smoke | pass |
| Landing quota (stubbed) | 5→5→5→5→5→4 |

---

## 28. Display-only chat answer lines

### Scope

Backend already exposed `OffenseDateUsed` on mapping / section_lookup schemas; this pass wires resolve-bifurcation returns, adds client i18n + ChatEntry rendering (offence-date line, scope, Exception/Proviso notice, Context strip, language-switch note), and leaves Stage 1–4 logic, retrieval, bifurcation margin, prompts, and verifier unchanged.

### Backend

- `_run_pipeline` continues to build `odu` and attach via `_finish` on all paths (mapping, section_lookup, bifurcation, clarify, failure).
- `resolve_bifurcation`: rebuild or reuse pending `offense_date_used`; pass into `_build_mapping` / `_build_section_lookup_from_chunks`; wrap with `_attach_offense_date_used`. Date-conflict re-run passes `date_source="message"`.

### Frontend

- i18n: `offenseDateUsedLine`, source parentheticals, `exceptionProvisoNotice`, `scopeLine`, `langSwitchNote` + language names; HI/MR `mappingPhraseMerged` shortened to avoid doubled में/मध्ये (templates in `/tmp/lawshift_hi_mr_mapping_templates.txt`).
- `ChatEntry`: structured `offense_date_used` near top of mapping / section cards; skip duplicate `dateLockNote` when present; strip `[Context:…]` in expanded statute text; scope after verification; exception notice when source text matches `\b(Exception|Explanation|Proviso)\b`; one-shot language note on toggle when thread has assistant content.

### Scripts / results

| Script | Purpose |
|--------|---------|
| `/tmp/lawshift_display_corpus.py` | Count IPC/BNS/BNSS sections with Exception/Explanation/Proviso; Context strip samples |
| `/tmp/lawshift_display_verify.py` | API smoke: plain map, lock+20 June, date-conflict resolve, range phrase; prints `offense_date_used` |
| `/tmp/lawshift_display_regress.py` | Diagnosis 9, false-block 285=0, Stage 1 44/44, Recall@5 0.841, quota stub 5→5→5→5→4 |

| Check | Result |
|--------|--------|
| Corpus Exception/Explanation/Proviso (`\b(Exception\|Explanation\|Proviso)\b` on section text) | **IPC 72/562** (`ipc_statutes.jsonl`, `IPC_*`); **BNS 79/358**; **BNSS 33/531** (`statutes.jsonl`, `BNS_*` / `BNSS_*`); **BSA 30/170** (`BSA_*`, display-only). All **1059** `statutes.jsonl` rows carry `[Context:…]`; IPC rows have no Context prefix. **30/30** random strip samples (seed 42) start with section number after `^\[Context:[^\]]*\]\s*` removal |
| API verify: lock map then 20 June (same IPC side) | second turn **`mapping`** (not `date_conflict`); `date_lock_label` **25 June 2024**; `offense_date_used` **`{label: 25 June 2024, code: IPC, source: earlier_message}`** |
| API verify: “between 25 June and 5 July 2024” | `mapping` → `{label: 5 July 2024, code: BNS, source: message}` |
| API verify: date-conflict resolve (control) | `mapping` → `{label: 25 June 2024, code: IPC, source: message}` |
| HI/MR `mappingPhraseMerged` | **विलीन है** / **विलीन आहे** (no doubled में/मध्ये in phrase token) |
| `lawshift_display_regress.py` (`.venv/bin/python`) | diagnosis **9/9**; false-block **285 = 0**; Stage 1 **44/44**; Recall@5 **0.841**; landing quota stub **pass** → `/tmp/lawshift_display_regress_out.json` |

---

## 29. Fixed Conclusion (code-written)

### Problem

The Stage 4 writer’s Conclusion often asserted guilt or punishment (“should be punished”, “is guilty”, …) from incomplete facts. The 14B verifier only sees Rule + Conclusion, so Application fabrications stayed invisible. Earlier **0-of-40 fabricated** (hand review) and the **15-of-40 flagged** verifier figures describe the **generated** Conclusion era.

### Change

When `LAWSHIFT_FIXED_CONCLUSION` is on (default **1**), `_build_mapping` discards the writer Conclusion and sets:

`On the facts described, this appears to fall within <code> <section> (<heading>).`

Heading from `stage3.option_description` (same as bifurcation options). Issue / Rule / Application unchanged. Response adds `fixed_conclusion: {code, section, heading}` for client templates. Verifier code/prompt unchanged; it receives Rule + **this fixed** Conclusion. Stage 5 skips translating `conclusion` (`skip_fields={"conclusion"}`); HI/MR use i18n `fixedConclusion` (agent drafts, native review). ChatEntry renders the template from the structured parts (including on language switch). At **0**, the generated Conclusion is shown exactly as before.

Env read: `app/main.py` → `_fixed_conclusion_enabled()`.

### Numbers (see `results/fixed_conclusion.json`)

| Check | Result |
|--------|--------|
| Fact-20 guilty phrase hits in **Conclusion** (switch **1**, fixed sentence) | **0** hits / 20 |
| Fact-20 guilty phrase hits in **Conclusion** (switch **0**, fresh `generate_irac`) | **14** hits / 11 Conclusions (stored v1 ref: **13**/20; **31** full-IRAC hits in wording JSON) |
| Verifier `verify_rule_only_14b_v2` on Rule + **fixed** Conclusion (gold 40) | **12** / 40 NOT_SUPPORTED vs **15** / 40 before (generated Conclusions) |
| Same verifier (fact 20) | **2** / 20 NOT_SUPPORTED |
| Known-bad five with fixed Conclusion | **6**, **9** SUPPORTED; **12**, **13**, **39** NOT_SUPPORTED |
| Rule span ⊈ section (same 60 outputs, whitespace/ellipsis-tolerant) | **5** failures (section numbers only): 115, 22, 292, 433, 506 |
| Application legal-test phrase from section absent from user message (same 60) | **5** (examples in JSON) |
| Regressions (in-process TestClient + stored Stage 1 / Recall) | diagnosis **9/9**; fact-free **25** missing_facts + **5** ISO missing_date; false-block **0/285**; Stage 1 **44/44**; Recall@5 **0.841**; bif85 recount **52**/85 (prior baseline **47**, margin unchanged); code-mismatch **6/6**; section_lookup **7/7**; date-conflict + rejected-options pass; quota stub **5→5→5→5→4** |

Harnesses under `/tmp` (`lawshift_fixed_concl_master.py`, `lawshift_fixed_concl_offline.py`, `lawshift_fixed_concl_regress.py`); verifier detail `/tmp/lawshift_fixed_concl_6b.json`.

Plain statement: prior **0-of-40 fabricated** and **15-of-40 flagged** verifier results describe the **generated** Conclusion; they are not scores for the fixed sentence. With the fixed sentence the verifier can still catch Rule↔heading mismatch, but not Application fabrications or guilt wording.

---

## 30. Translation number guard (HI/MR)

### Problem

IndicTrans2 can change digit sequences in Issue / Rule / Application. Observed: Hindi Application for “Section 302 IPC … he killed a man” said **धारा 307** (attempt) while English said **Section 302** (murder). Conclusion was already fixed / not machine-translated (§29).

### Change

Pure check in `app/translation_number_guard.py`: after each field is translated, compare digit multisets (ASCII + Devanagari → ASCII). On mismatch, keep the English field and append the name to `translation_fallback_fields` on `MappingResponse`. Wired in `translate_irac` only (Stages 1–4, verifier, models, fixed Conclusion untouched).

**List markers ignored:** 1–2 digit `(n)` without a nearby section cue, or `n.` / `n)` at line start. Section cues (`section` / IPC / BNS / BNSS / BSA / धारा / कलम / §) keep the number in the multiset. Unit tests: `tests/test_translation_number_guard.py`.

Frontend: one-line note when any field fell back (`numberGuardFallbackNote`; HI/MR agent drafts, native review).

### Numbers (`results/number_guard_measure.json`)

| Check | Result |
|--------|--------|
| Raw drift on 100 stored/generated IRACs × HI (issue/rule/application) | **0** / 300 fields |
| Raw drift on same × MR | **1** / 300 (Rule on gold40_14: translator **added** 16, 1908; not a section swap) |
| Guard on those 100 | HI **0** answers fall back; MR **1** (rule) |
| Kill-case raw HI Application 302→307 | **5** / 5 trials |
| Kill-case with guard HI / MR | fallback **4**/5 HI (Application kept English 302); **0**/5 MR |
| Regression | diagnosis **9/9**; false-block **0**/285; Stage 1 **44**/44; Recall@5 **0.841**; quota **5→5→5→5→4**; English answer unchanged; HI smoke falls back Application |

Worth the cost: rare on the broad 100-set, but the murder/302 Hindi path drifts almost every time without the guard; the check is a cheap pure function.

---

## 31. How to run the regression suite

Checked-in under `scripts/regression/`. Calls `handle_query` / `resolve_bifurcation` in-process (no frontend, no live backend on :8000). Stage 4 writer/verifier and Stage 5 translation are stubbed so Ollama is not required. Stage 3 embeddings still load from `models/finetuned-bge-small-ipc-bns-e8`.

```bash
# from repo root
.venv/bin/python scripts/regression/run_all.py
```

Progress: `/tmp/lawshift_regression_prog.txt`. Full details: `/tmp/lawshift_regression_out.json`. Per-question bif85 statuses (for future diffs): `results/regression_baseline.json`. Hard timeout: `REGRESSION_TIMEOUT_SEC` (default 3600).

Expectations live in JSON next to the runner (`expectations.json`, `fact_free_30.json`, `diagnosis_9.json`, `code_mismatch_6.json`, `section_lookup_7.json`, `date_conflict_cases.json`, `rejected_options_cases.json`, `bif85_questions.json`, `false_block_200.json`, `false_block_sources.json`). Aggregate numbers are not rewritten when a run differs — the runner reports FAIL and the delta.

Checks covered: diagnosis 9; fact-free 30; false-block 285 (85 plain + 200 held-out); Stage 1 44; **two** Recall@5 checks on `data/splits/test.jsonl` (paper + production); bif85_labeled (48/85) plus informational first-85 count; code-mismatch 6; section_lookup 7; date-conflict; rejected-options; quota stub `[5,5,5,5,4]` (mirrors `ChatEntry`, no browser).

**Paper vs production retrieval.** Paper Recall@5 **0.8412** (535/636) uses `src/finetune_more.py` `build_cascade` / `evaluate_cascade`: a non–act-aware `SECTION_PATTERN` short-circuit that promotes every chunk with the matched section number on `statutes.jsonl`. Production Recall@5 **0.8381** (533/636) uses `stage3.cascade_search_act_aware` (act-scoped exact match). The two-hit gap is indexes **565** and **628**: questions like “Section 300 of BNSS 2023” / “Section 156 of BSA 2023”, where act-aware `extract_act_scoped_numbers` treats the year **2023** as the section and misses the real short-circuit.

**Two 85-question bifurcation sets.** Asserted `bif85_labeled` is the single-citation labelled subset (`bif85_questions.json`), date `" 25 June 2024"`, IPC, margin 0.10 → **48**/85. The first 85 lines of `nyaya_eval_filtered.jsonl` under the same date/margin are informational only (**52** at last count); they overlap the labelled set only partly (59 shared / 26 unique each way).

---

## 32. Public API hardening (auth, limits, CORS)

### Problem

The FastAPI surface used `allow_origins=["*"]`, exposed `/docs`, returned internal counts from `/health`, and left `/api/query`, resolve, upload, map, and rulings unauthenticated with no body/upload size caps or generation concurrency control.

### Change (scope: `app/`, `tests/`, `requirements-backend.txt` only)

- **Auth** (`app/auth_supabase.py`): Bearer JWT; prefer project JWKS at `{SUPABASE_URL}/auth/v1/.well-known/jwks.json` (this project publishes **ES256**); fall back to `SUPABASE_JWT_SECRET` (HS256) when JWKS is empty. Offline tests use `LAWSHIFT_JWT_TEST_PUBLIC_KEY_PEM`. Checks signature, `exp`, `aud` (default `authenticated`). Optional on `/api/query` and `/api/query/resolve_bifurcation`; required on `/api/upload_document`. Bad/expired → clean 401. Pipeline return shapes unchanged; `handle_query` / `resolve_bifurcation` stay callable in-process without HTTP deps.
- **Limits** (`app/limits.py`): per-IP hourly caps on `/api/query` (anon 12 / auth 120); generation semaphore (default 2, wait 45 s → 503 `busy, try again`); upload ≤ 10 MB with magic-byte type sniff (PDF/JPEG/PNG); other POST bodies ≤ 100 KB. Client IP from left-most `X-Forwarded-For` only when `LAWSHIFT_TRUST_PROXY=1`.
- **CORS / docs / health**: `LAWSHIFT_ALLOWED_ORIGINS` (default `http://localhost:3000`); `/docs`, `/redoc`, `/openapi.json` off unless `LAWSHIFT_ENABLE_DOCS=1`; `/health` → `{"status":"ok"}` only.
- **Tests**: `tests/test_security_hardening.py` (local RSA keys; no network).
- **Regression (hardening):** `optional_auth` / `require_auth` took `SecuritySettings | None = None`, so FastAPI treated settings as a second body model and nested `/api/query` under `req` (422). Fixed by reading settings only via `get_settings()` inside the deps.
- **HTTP tests:** `tests/test_http_query_routes.py` hits the real routes with TestClient and stubbed `handle_query` / `resolve_bifurcation` (flat body 200, token 200, bad token 401, empty 422, resolve body, anon 429).

### Numbers

| Check | Result |
|--------|--------|
| `pytest tests/test_security_hardening.py` | **18** passed |
| `scripts/regression/run_all.py` | **PASS=12 FAIL=0 INFO=1** (diagnosis 9/9; fact-free 27+3; false-block 0/285; Stage 1 44/44; paper Recall 0.8412; production Recall 0.8381; bif85_labeled 48/85; code-mismatch 6/6; section_lookup 7/7; date-conflict 3/3; rejected-options 1/1; quota [5,5,5,5,4]) |

---

## 33. M3 — document extract + case attach (no pipeline on upload)

### Design

Logged-in extract only (`POST /api/documents/extract`); browser stores the file in Supabase. User confirms date/facts, then `POST /api/case/attach` locks the date and keeps facts in server memory (2 h TTL, 200 conversations, owner-checked). Follow-ups use the normal pipeline with facts appended after the message. `POST /api/case/detach` clears facts + lock. Legacy `/api/upload_document` still extracts then runs the pipeline via shared `extract_document`.

### Change (scope: `app/`, `tests/`, `scripts/regression/`, `requirements-backend.txt`, `PROCESS_LOG.md`)

- `app/stage0_document.py`: unified `extract_document`; PDF typed + OCR (&lt;40 chars/page, ≤30 pages, ≤10 OCR pages); DOCX via `python-docx` (reject macros / zip bombs); images ≤40 MP, OCR eng, 90 s budget; text normalised, truncated at 20k; Stage 1 date candidates (≤5).
- `app/case_attach.py` + routes; `handle_query` branch when attached (Stage 1 on follow-up only; `offense_date_used` source `document`|`confirmed`; missing-facts counts facts).
- **Attach retrieval (follow-up):** if the follow-up has no content words after the missing-facts meta strip (e.g. “Which section applies?”), Stage 3 searches the **facts alone**; otherwise follow-up first, then facts. Writer/gates always get the full follow-up + facts. No automatic character cut (a 500–800 cap helped only when facts sat at the start of a pad; it hurt middle/end). Typed path unchanged (`retrieve_query` defaults to `message`).
- Limits: `LAWSHIFT_EXTRACT_PER_HOUR` (10), `LAWSHIFT_MAX_CONCURRENT_EXTRACT` (1), `LAWSHIFT_EXTRACT_WAIT_SEC` (20).
- Tests: `tests/test_documents_m3.py`. Gold measure: `scripts/regression/measure_attach_gold.py` → `/tmp/lawshift_m3_gold_out.json`; FIR docs under `/tmp/lawshift_m3_fir_docs/`.

### Numbers (gold hit rates)

**Part 1 — 85 labelled questions** (BNS-side date for BNS/BNSS/BSA gold; modes a–d):

| Mode | top5 | top1 | bif options contain gold (when bif) |
|------|------|------|-------------------------------------|
| a typed+date | 54/85 (0.635) | 37/85 (0.435) | 22/49 (0.449) |
| b facts only | 56/85 (0.659) | 36/85 (0.424) | 23/47 (0.489) |
| c follow-up first (old attach) | 56/85 (0.659) | 39/85 (0.459) | 25/48 (0.521) |
| d follow-up after facts | 56/85 (0.659) | 38/85 (0.447) | 23/47 (0.489) |
| after: meta→facts (= b) | 56/85 (0.659) | 36/85 (0.424) | 23/47 (0.489) |

**Part 2 — 40×FIR wrappers** (20 IPC-mapped + 20 BNS; 800/1500/3000/6000 × start/middle/end; n=480 per mode):

| Mode | top5 | top1 |
|------|------|------|
| b facts only / **after meta→facts** | 114/480 (0.238) | 58/480 (0.121) |
| c follow-up first (before) | 92/480 (0.192) | 47/480 (0.098) |
| first 500 chars only | 47/480 (0.098) | 7/480 (0.015) |

By length (mode b / after): 800 → 0.333 top5; 1500 → 0.275; 3000 → 0.233; 6000 → 0.108. Blind first-500 is **0** top5 when facts are at the end.

| Check | Result |
|--------|--------|
| `pytest tests/` | **59** passed |
| Regression (nothing attached) | **PASS=12 FAIL=0 INFO=1** (unchanged) |
| Offer “ask which section applies?” on full FIR text? | **No** — ~24% top5 vs ~66% on short plain questions. Prefer: user writes a short facts summary; document supplies the date (and optional context). Guidance: “Write two or three sentences about what happened (who did what, and to whom).” Aim for **about 800 characters** of facts, not the whole FIR. |

---

*End of process log. Generated from files in `results/` as of the unified comparison run, plus GovIntel README figures verified against the live Hugging Face card, plus the split-offense review and `split_detector_v2_eval.json`, Stage 4 generation and verifier evals (§16), citation-fix verifier evaluation (§17), backend integration / bifurcation validation (§18), multilingual Stage 5 / IndicTrans2 fix (§19), Ollama Metal / Rosetta fix and Stage 4 warm-up (§20), landing-page + live chat UI verification (§21), missing-facts gate (§22), IPC↔BNS code-mismatch intercept (§23), citation-only section lookup / bifurcation escape / date-lock diagnosis (§24), locked-date conflict handling (§25), Stage 4 conclusion-wording variant (§26), bifurcation-escape / cited-section / mismatch-card rules (§27), display-only chat answer lines (§28), fixed Conclusion (§29), translation number guard (§30), the checked-in regression suite (§31), public API hardening (§32), and M3 document extract/attach (§33).*
