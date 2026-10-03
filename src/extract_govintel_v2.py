import json, re
import pandas as pd
from huggingface_hub import hf_hub_download

path = hf_hub_download("aashnasharma/govintel-legal-dataset", "data/train.jsonl", repo_type="dataset")
with open(path) as f:
    lines = [json.loads(l) for l in f]

statutes = pd.read_json("data/clean/statutes.jsonl", lines=True)
valid_lookup = {}
for _, row in statutes.iterrows():
    key = (row["act"].split()[0].upper(), str(row["section_number"]).strip())
    valid_lookup[key] = row["chunk_id"]

ACT_NAMES = {
    "BNS": r"(?:BNS\s*,?\s*2023|Bharatiya\s+Nyaya\s+Sanhita\s*,?\s*2023?)",
    "BNSS": r"(?:BNSS\s*,?\s*2023|Bharatiya\s+Nagarik\s+Suraksha\s+Sanhita\s*,?\s*2023?)",
    "BSA": r"(?:BSA\s*,?\s*2023|Bharatiya\s+Sakshya\s+Adhiniyam\s*,?\s*2023?)",
}
SEC_NUM = r"\d+[A-Za-z]{0,3}(?:\([^)]{0,10}\))?"
SEC_LIST = rf"({SEC_NUM}(?:\s*,\s*{SEC_NUM})*(?:\s*,?\s*and\s+{SEC_NUM})?)"

def split_numbers(block):
    parts = re.split(r",|\band\b", block)
    return [p.strip() for p in parts if p.strip()]

def find_citations(text):
    found = {}  # act -> set of section numbers
    for act, act_pat in ACT_NAMES.items():
        # Pattern A: "Section(s) X[, Y, and Z] of the <act>"
        for m in re.finditer(rf"Sections?\s+{SEC_LIST}\s+of\s+the\s+{act_pat}", text, re.IGNORECASE):
            nums = split_numbers(m.group(1))
            found.setdefault(act, set()).update(nums)
        # Pattern B: "<act> Section X" (short form, act first)
        for m in re.finditer(rf"{act_pat}\s*,?\s*Section\s+({SEC_NUM})", text, re.IGNORECASE):
            found.setdefault(act, set()).add(m.group(1))
    # Pattern C: split "Applicable statute: X" / "Applicable section: Section Y"
    stat_m = re.search(r"Applicable statute:\s*([^\n]+)", text, re.IGNORECASE)
    sec_m = re.search(rf"Applicable section:\s*Section\s+({SEC_NUM})", text, re.IGNORECASE)
    if stat_m and sec_m:
        for act, act_pat in ACT_NAMES.items():
            if re.search(act_pat, stat_m.group(1), re.IGNORECASE):
                found.setdefault(act, set()).add(sec_m.group(1))
    return found

extracted = []
zero_hits = multi_hits = 0
for record in lines:
    messages = record.get("messages", [])
    user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
    assistant_msg = next((m["content"] for m in messages if m["role"] == "assistant"), None)
    if not user_msg or not assistant_msg:
        continue

    found = find_citations(assistant_msg)
    total_sections = sum(len(v) for v in found.values())

    if total_sections == 0:
        zero_hits += 1
        continue
    if total_sections > 1:
        multi_hits += 1
        continue

    act, secs = next(iter(found.items()))
    sec = next(iter(secs))
    key = (act, sec)
    if key in valid_lookup:
        extracted.append({"question": user_msg, "chunk_id": valid_lookup[key], "act": act, "section": sec})

extracted_df = pd.DataFrame(extracted)
extracted_df.to_json("data/clean/govintel_extracted_v2.jsonl", orient="records", lines=True)

print(f"Total records: {len(lines)}")
print(f"Zero-hit (no BNS/BNSS/BSA citation found): {zero_hits}")
print(f"Multi-hit (ambiguous, dropped): {multi_hits}")
print(f"Extracted (single, unambiguous, valid section): {len(extracted_df)}")
print(f"Yield: {len(extracted_df)/len(lines):.1%}")

# Re-run contamination check against nyaya-eval-v0 with the larger extracted set
nyaya = pd.read_json("data/clean/nyaya_eval_filtered.jsonl", lines=True)
def jaccard(a, b):
    wa, wb = set(a.lower().split()), set(b.lower().split())
    return len(wa & wb) / max(1, len(wa | wb))

overlaps = []
for _, row in extracted_df.iterrows():
    for nq in nyaya["question"]:
        if jaccard(row["question"], nq) > 0.5:
            overlaps.append({"govintel_q": row["question"], "nyaya_q": nq})

print(f"\nContamination check (v2 extraction vs nyaya-eval-v0): {len(overlaps)} overlap pairs")
with open("results/govintel_extraction_v2_report.json", "w") as f:
    json.dump({
        "total_records": len(lines), "zero_hits": zero_hits, "multi_hits": multi_hits,
        "extracted_count": len(extracted_df), "yield_pct": round(len(extracted_df)/len(lines), 4),
        "contamination_overlaps": len(overlaps),
    }, f, indent=2)
