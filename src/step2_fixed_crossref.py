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

lookup_by_section = {}
for _, row in statutes.iterrows():
    key = (row["act"], str(row["section_number"]).strip())
    lookup_by_section[key] = row["chunk_id"]

# Fixed pattern: catches "section 433" (singular) AND
# "sections 32, 72, 74, 76, 79, 80 and 81" (plural lists, comma/and/& separated)
LIST_PATTERN = re.compile(
    r'sections?\s+((?:\d+[A-Za-z]{0,3}\s*(?:,|and|&|or)?\s*)+)',
    re.IGNORECASE
)
NUM_PATTERN = re.compile(r'\d+[A-Za-z]{0,3}')

def find_cross_refs(text, act, own_section):
    refs = set()
    for list_match in LIST_PATTERN.finditer(text):
        block = list_match.group(1)
        for num_match in NUM_PATTERN.finditer(block):
            num = num_match.group(0)
            if num == str(own_section).strip():
                continue
            key = (act, num)
            if key in lookup_by_section:
                refs.add(lookup_by_section[key])
    return list(refs)

cross_ref_map = {}
ref_counts = []
for _, row in statutes.iterrows():
    refs = find_cross_refs(row["text"], row["act"], row["section_number"])
    cross_ref_map[row["chunk_id"]] = refs
    ref_counts.append(len(refs))

statutes["n_cross_refs_found"] = ref_counts
n_with_refs = (statutes["n_cross_refs_found"] > 0).sum()
total_ref_links = sum(ref_counts)

print(f"Sections with at least one resolved cross-reference: {n_with_refs} / {len(statutes)}")
print(f"Total cross-reference links found: {total_ref_links}")
print(f"(Previous regex found cross-refs in 319 sections — compare against that)")

with open("data/clean/cross_ref_map.json", "w") as f:
    json.dump(cross_ref_map, f, indent=2)
print("Cross-reference map saved to data/clean/cross_ref_map.json — for Stage 4 use, NOT for modifying Stage 3 retrieval corpus text.")

# ---------- Re-run retrieval on ORIGINAL corpus only (Step 1 augmentation approach is dropped) ----------

chunk_ids = statutes["chunk_id"].tolist()
section_numbers = statutes["section_number"].astype(str).str.strip().tolist()
texts = statutes["text"].tolist()

model = SentenceTransformer("models/finetuned-bge-small-ipc-bns-e8")
print("Encoding original corpus...")
corpus_emb = model.encode(texts, show_progress_bar=True)

SECTION_PATTERN = re.compile(r'(?:section|sec\.?|§|ipc|bns|bnss|bsa)\s*[:#]?\s*(\d+[a-zA-Z]{0,3})', re.IGNORECASE)

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

def is_relaxed_hit(gold, retrieved_list):
    if gold in retrieved_list:
        return True, "strict"
    gold_refs = set(cross_ref_map.get(gold, []))
    for r in retrieved_list:
        if r in gold_refs:
            return True, "relaxed_via_crossref"
    return False, "miss"

strict_hits, relaxed_hits = [], []
relaxed_via_crossref_count = 0
for _, row in val.iterrows():
    gold = row["chunk_id"]
    retrieved = cascade_search(row["question"], k=5)
    strict_hit = gold in retrieved
    relaxed_hit, kind = is_relaxed_hit(gold, retrieved)
    strict_hits.append(strict_hit)
    relaxed_hits.append(relaxed_hit)
    if kind == "relaxed_via_crossref":
        relaxed_via_crossref_count += 1

strict_recall = float(np.mean(strict_hits))
relaxed_recall = float(np.mean(relaxed_hits))

results = {
    "n": len(val),
    "sections_with_crossrefs": int(n_with_refs),
    "total_crossref_links": int(total_ref_links),
    "strict_recall_at_5": strict_recall,
    "relaxed_recall_at_5": relaxed_recall,
    "additional_hits_from_relaxed_metric": relaxed_via_crossref_count,
    "prior_run_for_comparison": {
        "sections_with_crossrefs": 319,
        "strict_recall_at_5": 0.8299,
        "relaxed_recall_at_5": 0.8425,
        "additional_hits": 8,
    },
}
with open("results/cross_reference_step2_fixed_eval.json", "w") as f:
    json.dump(results, f, indent=2)

report = f"""# Fixed Cross-Reference Regex — Audit Report

## Objective
Re-measure relaxed recall@5 after fixing the cross-reference detector to catch plural
"sections X, Y and Z" lists (previous version only caught singular "section N").
Retrieval runs on the ORIGINAL, unaugmented corpus — Step 1's corpus-text-merging
approach has been dropped after it reduced strict recall in the prior run.

## Method
- Model: models/finetuned-bge-small-ipc-bns-e8 (unchanged)
- Eval set: data/splits/val.jsonl (n={len(val)}), test untouched
- Cross-reference detector: now matches both "section N" and "sections N, M and P" style lists

## Results

| Version | Sections w/ cross-refs | Strict Recall@5 | Relaxed Recall@5 | Extra hits |
|---|---:|---:|---:|---:|
| Previous (singular-only regex) | 319 | 0.8299 | 0.8425 | 8 |
| Fixed (singular + plural lists) | {n_with_refs} | {strict_recall:.4f} | {relaxed_recall:.4f} | {relaxed_via_crossref_count} |

## Observations
- Cross-reference detection coverage change: {n_with_refs - 319:+d} sections (previously 319)
- Relaxed recall change vs previous fixed-regex attempt: {relaxed_recall - 0.8425:+.4f}
- Strict recall should be unchanged or very close to the original 0.8299 baseline, since
  retrieval itself was not modified in this run — only the cross-reference map used for
  the relaxed metric changed.
"""
with open("results/cross_reference_step2_fixed_report.md", "w") as f:
    f.write(report)

print(report)
