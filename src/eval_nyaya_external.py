"""Evaluate original-e8 vs combined-e5 on nyaya-eval-v0.

Evaluation-only: does not read or write train/val/test splits.
Gold chunk_ids are extracted from expected_answer / required_facts using the
same citation style as src/extract_govintel_v2.py, plus nyaya shorthand
("Section 75 BNS", "BNSS (Section 173)"), then mapped onto statutes.jsonl.
"""
import json
import os
import re

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

nyaya = pd.read_json("data/clean/nyaya_eval_filtered.jsonl", lines=True)
statutes = pd.read_json("data/clean/statutes.jsonl", lines=True)

valid_lookup = {}
for _, row in statutes.iterrows():
    key = (row["act"].split()[0].upper(), str(row["section_number"]).strip())
    valid_lookup[key] = row["chunk_id"]

# Same act/section style as extract_govintel_v2.py; 2023 is optional so
# nyaya shorthand ("Section 75 BNS") still matches. Word boundaries stop
# BNS from eating BNSS.
ACT_NAMES = {
    "BNS": r"(?:BNS(?:\s*,?\s*2023)?\b|Bharatiya\s+Nyaya\s+Sanhita\s*,?\s*2023?)",
    "BNSS": r"(?:BNSS(?:\s*,?\s*2023)?\b|Bharatiya\s+Nagarik\s+Suraksha\s+Sanhita\s*,?\s*2023?)",
    "BSA": r"(?:BSA(?:\s*,?\s*2023)?\b|Bharatiya\s+Sakshya\s+Adhiniyam\s*,?\s*2023?)",
}
SEC_NUM = r"\d+[A-Za-z]{0,3}(?:\([^)]{0,10}\))?"
SEC_LIST = rf"({SEC_NUM}(?:\s*,\s*{SEC_NUM})*(?:\s*,?\s*and\s+{SEC_NUM})?)"


def split_numbers(block):
    parts = re.split(r",|\band\b", block)
    return [p.strip() for p in parts if p.strip()]


def normalize_sec(sec):
    """Map 103(1) -> 103 so uniqueness is at the statutes chunk_id grain."""
    return re.sub(r"\([^)]*\)$", "", sec).strip()


def find_citations(text):
    found = {}
    for act, act_pat in ACT_NAMES.items():
        # Pattern A: "Section(s) X[, Y] of the <act>"
        for m in re.finditer(rf"Sections?\s+{SEC_LIST}\s+of\s+the\s+{act_pat}", text, re.IGNORECASE):
            found.setdefault(act, set()).update(split_numbers(m.group(1)))
        # Pattern B: "<act> Section X" / "BNSS (Section 173)"
        for m in re.finditer(rf"{act_pat}\s*[,()]?\s*Section\s+({SEC_NUM})", text, re.IGNORECASE):
            found.setdefault(act, set()).add(m.group(1))
        # Pattern D (nyaya shorthand): "Section 75 BNS"
        for m in re.finditer(rf"Sections?\s+({SEC_NUM})\s+{act_pat}", text, re.IGNORECASE):
            found.setdefault(act, set()).add(m.group(1))
    # Pattern C: split "Applicable statute" / "Applicable section"
    stat_m = re.search(r"Applicable statute:\s*([^\n]+)", text, re.IGNORECASE)
    sec_m = re.search(rf"Applicable section:\s*Section\s+({SEC_NUM})", text, re.IGNORECASE)
    if stat_m and sec_m:
        for act, act_pat in ACT_NAMES.items():
            if re.search(act_pat, stat_m.group(1), re.IGNORECASE):
                found.setdefault(act, set()).add(sec_m.group(1))
    return found


def citations_for_row(row):
    # Search fields separately so concatenating facts cannot invent
    # "BNS Section 66D" across a BNS cite and an IT Act cite.
    fields = [str(row.get("expected_answer", "") or "")]
    fields.extend(str(x) for x in (row.get("required_facts") or []))
    merged = {}
    for field in fields:
        for act, secs in find_citations(field).items():
            merged.setdefault(act, set()).update(normalize_sec(s) for s in secs)
    return merged


n_zero = n_multi = n_unmapped = 0
labeled_rows = []
for _, row in nyaya.iterrows():
    found = citations_for_row(row)
    total = sum(len(v) for v in found.values())
    if total == 0:
        n_zero += 1
        continue
    if total != 1:
        n_multi += 1
        continue
    act, secs = next(iter(found.items()))
    sec = next(iter(secs))
    chunk_id = valid_lookup.get((act, sec))
    if chunk_id is None:
        n_unmapped += 1
        continue
    rec = row.to_dict()
    rec["gold_extraction"] = (act, sec)
    rec["chunk_id"] = chunk_id
    labeled_rows.append(rec)

nyaya_labeled = pd.DataFrame(labeled_rows)
print(f"nyaya-eval-v0 filtered (BNS/BNSS/BSA): {len(nyaya)}")
print(f"Zero citation (dropped): {n_zero}")
print(f"Multi citation (dropped): {n_multi}")
print(f"Single citation, no statutes map (dropped): {n_unmapped}")
print(f"With extractable single gold section: {len(nyaya_labeled)}")

chunk_ids = statutes["chunk_id"].tolist()
section_numbers = statutes["section_number"].astype(str).str.strip().tolist()
texts = statutes["text"].tolist()

SECTION_PATTERN = re.compile(
    r"(?:section|sec\.?|§|ipc|bns|bnss|bsa)\s*[:#]?\s*(\d+[a-zA-Z]{0,3})",
    re.IGNORECASE,
)


def evaluate_model(model_path, label, k=5):
    model = SentenceTransformer(model_path)
    corpus_emb = model.encode(texts, show_progress_bar=True)

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

    hits, rr, ndcgs = [], [], []
    n_triggered = 0
    for _, row in nyaya_labeled.iterrows():
        gold = row["chunk_id"]
        retrieved = cascade_search(row["question"], k=k)
        if SECTION_PATTERN.search(row["question"]):
            n_triggered += 1
        hit = gold in retrieved
        rank = retrieved.index(gold) + 1 if hit else 0
        hits.append(hit)
        rr.append(1.0 / rank if rank else 0.0)
        ndcgs.append(1.0 / np.log2(rank + 1) if rank else 0.0)

    return {
        "label": label,
        "n": len(nyaya_labeled),
        "section_pattern_trigger_rate": float(n_triggered / len(nyaya_labeled)) if len(nyaya_labeled) else 0.0,
        "recall_at_5": float(np.mean(hits)),
        "mrr": float(np.mean(rr)),
        "ndcg_at_5": float(np.mean(ndcgs)),
    }


result_e8 = evaluate_model("models/finetuned-bge-small-ipc-bns-e8", "original-e8")
result_combined = evaluate_model("models/finetuned-bge-small-combined-e5", "combined-e5")

results = {
    "extraction": {
        "n_filtered_bns_bnss_bsa": int(len(nyaya)),
        "n_zero_citation": int(n_zero),
        "n_multi_citation": int(n_multi),
        "n_unmapped": int(n_unmapped),
        "n_labeled": int(len(nyaya_labeled)),
        "note": (
            "Gold extracted from expected_answer/required_facts with GovIntel-v2 "
            "Patterns A/B/C plus nyaya shorthand 'Section X BNS'. Subsections "
            "like 103(1) normalize to 103 before the single-unambiguous check "
            "and statutes lookup. Train/val/test splits were not used."
        ),
    },
    "original_e8": result_e8,
    "combined_e5": result_combined,
}
with open("results/nyaya_eval_external_validation.json", "w") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2))
