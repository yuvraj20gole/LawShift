"""Extract GovIntel temporal_law_application-style examples as Stage 1 test cases.

train.jsonl has no task_type field, so this filters by content: an explicit
calendar date in the user question and IPC/BNS routing language in the
assistant reply. Evaluation-only sample; does not touch train/val/test splits.
"""
import json
import random
import re
from huggingface_hub import hf_hub_download

path = hf_hub_download("aashnasharma/govintel-legal-dataset", "data/train.jsonl", repo_type="dataset")
with open(path) as f:
    lines = [json.loads(l) for l in f]

# Filter to records whose assistant reply discusses an offense date and a
# routing decision (IPC vs BNS) - these come from the temporal_law_application
# task type, but since train.jsonl has no task_type field (confirmed earlier),
# filter by content pattern instead: presence of an explicit date AND explicit
# "IPC"/"BNS" routing language in the assistant reply
DATE_PATTERN = re.compile(
    r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b|'
    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
    re.IGNORECASE
)
ROUTING_PATTERN = re.compile(r'\b(IPC|BNS)\b.{0,100}\b(applies|governs|applicable)\b', re.IGNORECASE)

candidates = []
for record in lines:
    messages = record.get("messages", [])
    user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
    assistant_msg = next((m["content"] for m in messages if m["role"] == "assistant"), None)
    if not user_msg or not assistant_msg:
        continue
    date_match = DATE_PATTERN.search(user_msg)  # date should be IN THE QUESTION, that's what Stage 1 extracts from
    routing_match = ROUTING_PATTERN.search(assistant_msg)
    if date_match and routing_match:
        candidates.append({
            "text": user_msg,
            "date_mentioned_in_question": date_match.group(0),
            "assistant_routing_discussion": assistant_msg[:300],
        })

print(f"Found {len(candidates)} GovIntel examples with an explicit date in the question and routing language in the answer")

random.seed(42)
sample = random.sample(candidates, min(30, len(candidates)))
with open("data/clean/stage1_real_test_cases.json", "w") as f:
    json.dump(sample, f, indent=2)

print(f"Wrote {len(sample)} cases to data/clean/stage1_real_test_cases.json")

for i, c in enumerate(sample[:10]):
    print(f"\n--- Example {i+1} ---")
    print("Question:", c["text"][:300])
    print("Date found in question:", c["date_mentioned_in_question"])
