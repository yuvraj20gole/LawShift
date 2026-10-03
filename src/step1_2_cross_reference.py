import pandas as pd
import numpy as np
import re
import json
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")

statutes = pd.read_json("data/clean/statutes.jsonl", lines=True)
val = pd.read_json("data/splits/val.jsonl", lines=True)

# ---------- STEP 1: Cross-reference corpus augmentation ----------

lookup_by_section = {}
for _, row in statutes.iterrows():
    key = (row["act"], str(row["section_number"]).strip())
    lookup_by_section[key] = row["chunk_id"]
text_by_chunk = dict(zip(statutes["chunk_id"], statutes["text"]))

REF_PATTERN = re.compile(r'section\s+(\d+[A-Za-z]{0,3})', re.IGNORECASE)

def find_cross_refs(text, act, own_section):
    refs = set()
    for m in REF_PATTERN.finditer(text):
        num = m.group(1)
        if num == str(own_section).strip():
            continue
        key = (act, num)
        if key in lookup_by_section:
            refs.add(lookup_by_section[key])
    return list(refs)

augmented_rows = []
cross_ref_map = {}  # chunk_id -> list of chunk_ids it references, saved for Step 2

for _, row in statutes.iterrows():
    refs = find_cross_refs(row["text"], row["act"], row["section_number"])
    cross_ref_map[row["chunk_id"]] = refs
    if refs:
        appended = "\n\n[Cross-referenced sections included below for context:]\n"
        for r in refs[:3]:
            appended += f"\n--- {r} ---\n{text_by_chunk[r][:800]}\n"
        augmented_text = row["text"] + appended
    else:
        augmented_text = row["text"]
    new_row = row.to_dict()
    new_row["text_augmented"] = augmented_text
    new_row["n_cross_refs_found"] = len(refs)
    augmented_rows.append(new_row)

aug_df = pd.DataFrame(augmented_rows)
aug_df.to_json("data/clean/statutes_augmented.jsonl", orient="records", lines=True)

with open("data/clean/cross_ref_map.json", "w") as f:
    json.dump(cross_ref_map, f, indent=2)

n_with_refs = (aug_df["n_cross_refs_found"] > 0).sum()
print(f"Sections with at least one resolved cross-reference: {n_with_refs} / {len(aug_df)}")

# ---------- Retrieval setup: strict vs augmented corpus ----------

chunk_ids = aug_df["chunk_id"].tolist()
section_numbers = aug_df["section_number"].astype(str).str.strip().tolist()

model = SentenceTransformer("models/finetuned-bge-small-ipc-bns-e8")

SECTION_PATTERN = re.compile(r'(?:section|sec\.?|§|ipc|bns|bnss|bsa)\s*[:#]?\s*(\d+[a-zA-Z]{0,3})', re.IGNORECASE)

def make_cascade(corpus_emb, texts_used_label):
    def cascade_search(query, k=5):
        results = []
        m = SECTION_PATTERN.search(query)
        if m:
            num = m.group(1)
            exact = [chunk_ids[i] for i, sn in enumerate(section_numbers) if sn == num]
            results.extend(exact)
        q_emb = model.encode([query])
        sims = cosine_similarity(q_emb, corpus_emb)[0]
        order = np.argsort(sims)[::-1]
        for i in order:
            cid = chunk_ids[i]
            if cid not in results:
                results.append(cid)
            if len(results) >= k:
                break
        return results[:k]
    return cascade_search

print("Encoding ORIGINAL corpus...")
orig_emb = model.encode(aug_df["text"].tolist(), show_progress_bar=True)
print("Encoding AUGMENTED corpus...")
aug_emb = model.encode(aug_df["text_augmented"].tolist(), show_progress_bar=True)

search_original = make_cascade(orig_emb, "original")
search_augmented = make_cascade(aug_emb, "augmented")

# ---------- STEP 2: Strict vs relaxed evaluation ----------

def is_relaxed_hit(gold, retrieved_list):
    """Hit if gold is retrieved directly, OR if any retrieved chunk is something
    the GOLD section's text explicitly cross-references (i.e. the retrieved
    section is a legitimate cross-referenced companion of the correct answer)."""
    if gold in retrieved_list:
        return True, "strict"
    gold_refs = set(cross_ref_map.get(gold, []))
    for r in retrieved_list:
        if r in gold_refs:
            return True, "relaxed_via_crossref"
    return False, "miss"

def evaluate(search_fn, label, k=5):
    strict_hits, relaxed_hits = [], []
    relaxed_via_crossref_count = 0
    for _, row in val.iterrows():
        gold = row["chunk_id"]
        retrieved = search_fn(row["question"], k=k)
        strict_hit = gold in retrieved
        relaxed_hit, kind = is_relaxed_hit(gold, retrieved)
        strict_hits.append(strict_hit)
        relaxed_hits.append(relaxed_hit)
        if kind == "relaxed_via_crossref":
            relaxed_via_crossref_count += 1
    return {
        "label": label,
        "n": len(val),
        "strict_recall_at_5": float(np.mean(strict_hits)),
        "relaxed_recall_at_5": float(np.mean(relaxed_hits)),
        "additional_hits_from_relaxed_metric": relaxed_via_crossref_count,
    }

print("Evaluating on ORIGINAL corpus (strict + relaxed)...")
result_original = evaluate(search_original, "original_corpus")
print("Evaluating on AUGMENTED corpus (strict + relaxed)...")
result_augmented = evaluate(search_augmented, "augmented_corpus")

results = {"original_corpus": result_original, "augmented_corpus": result_augmented}
with open("results/cross_reference_step1_2_eval.json", "w") as f:
    json.dump(results, f, indent=2)

# ---------- Audit report ----------

report = f"""# Cross-Reference Augmentation & Relaxed Metric — Audit Report

## Objective
Measure two independent things on the SAME held-out validation set (n={len(val)}), never touching test:
1. Does enriching each statute chunk with its cross-referenced sections' text improve strict retrieval (Step 1)?
2. Does crediting cross-referenced retrievals as valid hits reveal a higher "true" effective accuracy (Step 2)?

## Method
- Model: models/finetuned-bge-small-ipc-bns-e8 (unchanged, no retraining in this step)
- Eval set: data/splits/val.jsonl (n={len(val)}) — test set untouched
- Cross-reference detection: regex match on "section N" within each section's own text, resolved against the same Act's section table
- Sections with at least one resolved cross-reference: {n_with_refs} / {len(aug_df)}

## Results

| Corpus version | Strict Recall@5 | Relaxed Recall@5 | Additional hits credited by relaxed metric |
|---|---:|---:|---:|
| Original (unaugmented) | {result_original['strict_recall_at_5']:.4f} | {result_original['relaxed_recall_at_5']:.4f} | {result_original['additional_hits_from_relaxed_metric']} |
| Augmented (cross-refs merged into chunk text) | {result_augmented['strict_recall_at_5']:.4f} | {result_augmented['relaxed_recall_at_5']:.4f} | {result_augmented['additional_hits_from_relaxed_metric']} |

## Observations
- Step 1 impact (strict recall, original vs augmented corpus): {result_augmented['strict_recall_at_5'] - result_original['strict_recall_at_5']:+.4f}
- Step 2 impact (relaxed vs strict, on original corpus): {result_original['relaxed_recall_at_5'] - result_original['strict_recall_at_5']:+.4f}
- Both strict and relaxed numbers are reported here deliberately — the paper should present both, not just the higher one.
"""

with open("results/cross_reference_step1_2_report.md", "w") as f:
    f.write(report)

print(report)
