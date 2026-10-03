import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re, json
import os

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")

statutes = pd.read_json("data/clean/statutes.jsonl", lines=True)
val = pd.read_json("data/splits/val.jsonl", lines=True)

chunk_ids = statutes["chunk_id"].tolist()
texts = statutes["text"].tolist()
section_numbers = statutes["section_number"].astype(str).str.strip().tolist()
lookup = dict(zip(statutes["chunk_id"], statutes["text"]))

model = SentenceTransformer("models/finetuned-bge-small-ipc-bns-e8")
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

misses = []
for _, row in val.iterrows():
    gold = row["chunk_id"]
    retrieved = cascade_search(row["question"], k=5)
    if gold not in retrieved:
        misses.append({
            "question": row["question"],
            "question_type": row["question_type"],
            "gold_chunk_id": gold,
            "gold_text": lookup.get(gold, "MISSING FROM CORPUS"),
            "gold_answer": row["answer"],
            "retrieved_chunk_ids": retrieved,
            "retrieved_texts": [lookup.get(c, "") for c in retrieved],
        })

print(f"Total val questions: {len(val)}")
print(f"Total misses: {len(misses)}")
print(f"Miss rate: {len(misses)/len(val):.1%}")

# Sample 20 misses for manual review, stratified across question types where possible
misses_df = pd.DataFrame(misses)
parts = []
for qt, g in misses_df.groupby("question_type"):
    parts.append(g.sample(min(4, len(g)), random_state=42))
sample = pd.concat(parts, ignore_index=True).head(20)

with open("results/error_analysis_sample.md", "w") as f:
    f.write(f"# Error Analysis: {len(misses)} misses out of {len(val)} val questions ({len(misses)/len(val):.1%} miss rate)\n\n")
    f.write("For each miss: the question, the gold (expected) section, and what the model actually retrieved instead. Read each one and judge: is the retrieved answer plausibly also correct/related (defensible miss), or clearly wrong (real error)?\n\n")
    for i, row in enumerate(sample.to_dict("records")):
        f.write(f"## Miss {i+1} — {row['question_type']}\n\n")
        f.write(f"**Question:** {row['question']}\n\n")
        f.write(f"**Gold section ({row['gold_chunk_id']}):**\n> {row['gold_text'][:400]}...\n\n")
        f.write(f"**Gold answer (reference):** {row['gold_answer'][:300]}...\n\n")
        f.write(f"**Top-5 retrieved instead:**\n")
        for cid, txt in zip(row["retrieved_chunk_ids"], row["retrieved_texts"]):
            f.write(f"- `{cid}`: {txt[:200]}...\n")
        f.write(f"\n**Your judgment (fill in):** [ ] Clearly wrong  [ ] Plausibly related/defensible  [ ] Ambiguous/needs closer read\n\n---\n\n")

# Also save full miss list + a rough overlap heuristic to help prioritize reading order
def word_overlap(a, b):
    wa, wb = set(a.lower().split()), set(b.lower().split())
    return len(wa & wb) / max(1, len(wa | wb))

misses_df["top1_text_overlap_with_gold"] = misses_df.apply(
    lambda r: word_overlap(r["gold_text"], r["retrieved_texts"][0]) if r["retrieved_texts"] else 0, axis=1
)
misses_df.to_json("results/error_analysis_full.jsonl", orient="records", lines=True)

print(f"\nSample of 20 misses written to results/error_analysis_sample.md for manual review")
print(f"Full miss list ({len(misses)} rows) written to results/error_analysis_full.jsonl")
print(f"\nMiss rate by question type:")
print(misses_df["question_type"].value_counts())
