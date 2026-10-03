from datasets import load_dataset
from huggingface_hub import hf_hub_download
import json
import re
import pandas as pd

# Step 1 — Download nyaya-eval-v0, filter to BNS/BNSS/BSA only
nyaya = load_dataset("NyayaLabs98/nyaya-eval-v0", split="test")
nyaya_df = nyaya.to_pandas()
nyaya_bns = nyaya_df[nyaya_df["legal_domain"].isin(["bns", "bnss", "bsa"])].copy()
nyaya_bns.to_json("data/clean/nyaya_eval_filtered.jsonl", orient="records", lines=True)
print(f"nyaya-eval-v0 total: {len(nyaya_df)}, filtered to BNS/BNSS/BSA: {len(nyaya_bns)}")

# Step 2 — Inspect GovIntel's actual train.jsonl schema first (don't assume structure)
path = hf_hub_download("aashnasharma/govintel-legal-dataset", "data/train.jsonl", repo_type="dataset")
with open(path) as f:
    lines = [json.loads(l) for l in f]

print(f"Total GovIntel train rows: {len(lines)}")
print("Keys in first record:", list(lines[0].keys()))
print("First record (truncated):", json.dumps(lines[0], indent=2)[:1000])

# Step 3 — Extract clean question->section pairs
CLEAN_TYPES = {
    "section_explanation", "bns_seed_doctrinal", "bns_seed_interpretive",
    "bns_seed_relational", "bns_seed_scenario", "bns_seed_temporal",
    "offense_ingredients", "offense_elements", "punishment_and_defenses",
    "procedural_deep_dive", "cross_code_profile", "temporal_law_application",
}

statutes = pd.read_json("data/clean/statutes.jsonl", lines=True)
valid_lookup = {}
for _, row in statutes.iterrows():
    key = (row["act"].split()[0], str(row["section_number"]).strip())  # e.g. ("BNS", "103")
    valid_lookup[key] = row["chunk_id"]

SECTION_REF = re.compile(
    r'(?:Section|§)\s+(\d+[A-Za-z]{0,3})\s+of\s+the\s+(?:Bharatiya\s+\w+\s+\w+\s+)?(BNS|BNSS|BSA)|'
    r'(BNS|BNSS|BSA)\s+(?:Section|§)?\s*(\d+[A-Za-z]{0,3})',
    re.IGNORECASE
)

task_type_present = "task_type" in lines[0]
print(f"\ntask_type field present in records: {task_type_present}")

def extract_pairs(record):
    task_type = record.get("task_type") or ""
    if task_type_present and task_type not in CLEAN_TYPES:
        return None
    messages = record.get("messages", [])
    user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
    assistant_msg = next((m["content"] for m in messages if m["role"] == "assistant"), None)
    if not user_msg or not assistant_msg:
        return None

    matches = SECTION_REF.findall(assistant_msg)
    found_chunks = set()
    for m in matches:
        sec, act = (m[0], m[1]) if m[0] else (m[3], m[2])
        act = act.upper()
        key = (act, sec)
        if key in valid_lookup:
            found_chunks.add(valid_lookup[key])

    if len(found_chunks) == 1:
        return {"question": user_msg, "chunk_id": list(found_chunks)[0], "task_type": task_type}
    return None  # ambiguous (0 or 2+ sections found) -> drop

extracted = []
for record in lines:
    result = extract_pairs(record)
    if result:
        extracted.append(result)

extracted_df = pd.DataFrame(extracted)
extracted_df.to_json("data/clean/govintel_extracted.jsonl", orient="records", lines=True)

print(f"\nTotal GovIntel rows: {len(lines)}")
print(f"Successfully extracted (single unambiguous BNS/BNSS/BSA section): {len(extracted_df)}")
if len(extracted_df) and task_type_present:
    print("\nBreakdown by task_type:")
    print(extracted_df["task_type"].value_counts())

# Step 4 — Contamination check against nyaya-eval-v0
def jaccard(a, b):
    wa, wb = set(a.lower().split()), set(b.lower().split())
    return len(wa & wb) / max(1, len(wa | wb))

overlaps = []
nyaya_questions = nyaya_bns["question"].tolist()
for _, row in extracted_df.iterrows():
    for nq in nyaya_questions:
        sim = jaccard(row["question"], nq)
        if sim > 0.5:
            overlaps.append({"govintel_q": row["question"], "nyaya_q": nq, "similarity": sim})

print(f"\nPotential contamination pairs (Jaccard > 0.5): {len(overlaps)}")
for o in overlaps[:10]:
    print(json.dumps(o, indent=2))

with open("results/govintel_contamination_check.json", "w") as f:
    json.dump({
        "govintel_extracted_count": len(extracted_df),
        "nyaya_eval_filtered_count": len(nyaya_bns),
        "overlap_pairs_found": len(overlaps),
        "overlap_examples": overlaps[:10],
    }, f, indent=2)

print(f"\nSaved extraction to data/clean/govintel_extracted.jsonl")
print(f"Saved contamination report to results/govintel_contamination_check.json")
