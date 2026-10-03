import json
import re
import random
from huggingface_hub import hf_hub_download

path = hf_hub_download("aashnasharma/govintel-legal-dataset", "data/train.jsonl", repo_type="dataset")
with open(path) as f:
    lines = [json.loads(l) for l in f]

SECTION_REF = re.compile(
    r'(?:Section|§)\s+(\d+[A-Za-z]{0,3})\s+of\s+the\s+(?:Bharatiya\s+\w+\s+\w+\s+)?(BNS|BNSS|BSA)|'
    r'(BNS|BNSS|BSA)\s+(?:Section|§)?\s*(\d+[A-Za-z]{0,3})',
    re.IGNORECASE
)

failed = []
for record in lines:
    messages = record.get("messages", [])
    assistant_msg = next((m["content"] for m in messages if m["role"] == "assistant"), None)
    if not assistant_msg:
        continue
    matches = SECTION_REF.findall(assistant_msg)
    n_real_matches = sum(1 for m in matches if (m[0] or m[3]))
    if n_real_matches != 1:
        failed.append({"assistant_msg": assistant_msg, "n_matches": n_real_matches})

print(f"Failed extraction: {len(failed)} / {len(lines)}")
print(f"  Zero matches: {sum(1 for f in failed if f['n_matches']==0)}")
print(f"  Multiple matches: {sum(1 for f in failed if f['n_matches']>1)}")

random.seed(42)
sample = random.sample(failed, min(15, len(failed)))
for i, f in enumerate(sample):
    print(f"\n--- Failed example {i+1} (matches={f['n_matches']}) ---")
    print(f["assistant_msg"])
