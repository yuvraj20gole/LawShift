"""Compare raw full-text retrieval vs keyword-extracted short-phrase retrieval.

Zero-shot for original-e8 (never trained on GovIntel): 300 sampled questions
from data/clean/govintel_extracted_v2.jsonl against the statutes corpus.
"""
import json
import os
import random
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

govintel = pd.read_json("data/clean/govintel_extracted_v2.jsonl", lines=True)
statutes = pd.read_json("data/clean/statutes.jsonl", lines=True)

random.seed(42)
sample_idx = random.sample(range(len(govintel)), min(300, len(govintel)))
sample = govintel.iloc[sample_idx].reset_index(drop=True)
print(f"Testing on {len(sample)} real GovIntel questions (zero-shot for e8)")

# Reuse the same simple keyword-based action extractor from stage1_entity_extraction.py
ACTION_KEYWORDS = {
    "cheating": ["cheat", "tricked", "fraud", "deceive", "scam"],
    "theft": ["stole", "stolen", "theft", "took my"],
    "assault": ["hit", "slapped", "beat", "assault", "attacked"],
    "murder": ["killed", "murder"],
    "extortion": ["extort", "demanded money", "threatened to"],
    "criminal intimidation": ["threatened", "intimidat"],
    "defamation": ["defam", "spread false", "damaged my reputation"],
}


def extract_action_phrase(text):
    text_lower = text.lower()
    for action, keywords in ACTION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return action  # returns just the short category word, e.g. "cheating"
    return text  # fallback: no keyword matched, use full text anyway


chunk_ids = statutes["chunk_id"].tolist()
section_numbers = statutes["section_number"].astype(str).str.strip().tolist()
texts = statutes["text"].tolist()

model = SentenceTransformer("models/finetuned-bge-small-ipc-bns-e8")
print("Encoding corpus...")
corpus_emb = model.encode(texts, show_progress_bar=True)

SECTION_PATTERN = re.compile(
    r"(?:section|sec\.?|§|ipc|bns|bnss|bsa)\s*[:#]?\s*(\d+[a-zA-Z]{0,3})",
    re.IGNORECASE,
)


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


def evaluate(query_fn, label, k=5):
    hits, rr = [], []
    keyword_matched_count = 0
    for _, row in sample.iterrows():
        query = query_fn(row["question"])
        if query != row["question"]:
            keyword_matched_count += 1
        gold = row["chunk_id"]
        retrieved = cascade_search(query, k=k)
        hit = gold in retrieved
        rank = retrieved.index(gold) + 1 if hit else 0
        hits.append(hit)
        rr.append(1.0 / rank if rank else 0.0)
    return {
        "label": label,
        "n": len(sample),
        "recall_at_5": float(np.mean(hits)),
        "mrr": float(np.mean(rr)),
        "keyword_extraction_matched": keyword_matched_count,
    }


# Split uses citation phrasing only (section/sec/§ + number), not the cascade's
# broader ipc|bns|bnss|bsa trigger, so "has_section_number" means the exact-match
# giveaway is actually present in the question text.
CITATION_PATTERN = re.compile(
    r"(?:section|sec\.?|§)\s*[:#]?\s*(\d+[a-zA-Z]{0,3})",
    re.IGNORECASE,
)


def evaluate_subset(query_fn, label, subset_df, k=5):
    hits, rr = [], []
    for _, row in subset_df.iterrows():
        query = query_fn(row["question"])
        gold = row["chunk_id"]
        retrieved = cascade_search(query, k=k)
        hit = gold in retrieved
        rank = retrieved.index(gold) + 1 if hit else 0
        hits.append(hit)
        rr.append(1.0 / rank if rank else 0.0)
    n = len(subset_df)
    return {
        "label": label,
        "n": n,
        "recall_at_5": float(np.mean(hits)) if n else None,
        "mrr": float(np.mean(rr)) if n else None,
    }


if __name__ == "__main__":
    print("Evaluating: raw full question text...")
    result_raw = evaluate(lambda q: q, "raw_full_text")

    print("Evaluating: keyword-extracted short action phrase...")
    result_extracted = evaluate(extract_action_phrase, "keyword_extracted_phrase")

    results = {"raw_full_text": result_raw, "keyword_extracted_phrase": result_extracted}
    with open("results/legal_action_extraction_comparison.json", "w") as f:
        json.dump(results, f, indent=2)

    print(json.dumps(results, indent=2))

    sample["has_section_number"] = sample["question"].apply(
        lambda q: bool(CITATION_PATTERN.search(q))
    )
    print(f"Questions WITH explicit section number: {sample['has_section_number'].sum()}")
    print(f"Questions WITHOUT explicit section number: {(~sample['has_section_number']).sum()}")

    with_section = sample[sample["has_section_number"]]
    without_section = sample[~sample["has_section_number"]]

    print("Evaluating split: raw / keyword × with / without section number...")
    results_split = {
        "raw_WITH_section_number": evaluate_subset(lambda q: q, "raw_with_section", with_section),
        "raw_WITHOUT_section_number": evaluate_subset(lambda q: q, "raw_without_section", without_section),
        "keyword_WITH_section_number": evaluate_subset(extract_action_phrase, "kw_with_section", with_section),
        "keyword_WITHOUT_section_number": evaluate_subset(extract_action_phrase, "kw_without_section", without_section),
    }

    print(json.dumps(results_split, indent=2))
    with open("results/legal_action_confound_check.json", "w") as f:
        json.dump(results_split, f, indent=2)
