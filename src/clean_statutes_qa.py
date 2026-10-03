import pandas as pd
import re
import unicodedata
import json
from pathlib import Path

Path("data/clean").mkdir(parents=True, exist_ok=True)
Path("results").mkdir(exist_ok=True)

report = {}

def normalize_text(s):
    if not isinstance(s, str):
        return s
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

# ---------- Statutes ----------
statutes = pd.read_json("data/raw/statutes.jsonl", lines=True)
n_before = len(statutes)

statutes["text"] = statutes["text"].apply(normalize_text)
statutes["section_title"] = statutes["section_title"].apply(normalize_text)

null_text = statutes["text"].isna().sum()
statutes = statutes.dropna(subset=["text", "chunk_id"])
dupes = statutes.duplicated(subset=["chunk_id"]).sum()
statutes = statutes.drop_duplicates(subset=["chunk_id"], keep="first")

statutes.to_json("data/clean/statutes.jsonl", orient="records", lines=True)
report["statutes"] = {
    "rows_before": n_before,
    "rows_after": len(statutes),
    "null_text_dropped": int(null_text),
    "duplicate_chunk_ids_dropped": int(dupes),
    "act_breakdown": statutes["act"].value_counts().to_dict(),
}

# ---------- QA ----------
qa = pd.read_json("data/raw/qa.jsonl", lines=True)
n_before = len(qa)

qa["question"] = qa["question"].apply(normalize_text)
qa["answer"] = qa["answer"].apply(normalize_text)

null_rows = qa["question"].isna().sum() + qa["answer"].isna().sum()
qa = qa.dropna(subset=["question", "answer", "chunk_id"])
dupes = qa.duplicated(subset=["question", "chunk_id"]).sum()
qa = qa.drop_duplicates(subset=["question", "chunk_id"], keep="first")

# The critical check: does every QA chunk_id actually exist in the cleaned statutes file?
valid_ids = set(statutes["chunk_id"])
qa["chunk_id_valid"] = qa["chunk_id"].isin(valid_ids)
n_mismatched = (~qa["chunk_id_valid"]).sum()
mismatched_examples = qa[~qa["chunk_id_valid"]][["chunk_id", "question", "act", "section_number"]].head(15).to_dict("records")

qa_eval_ready = qa[qa["chunk_id_valid"]].drop(columns=["chunk_id_valid"])

qa.to_json("data/clean/qa_full.jsonl", orient="records", lines=True)
qa_eval_ready.to_json("data/clean/qa_eval_ready.jsonl", orient="records", lines=True)

report["qa"] = {
    "rows_before": n_before,
    "rows_after_cleaning": len(qa),
    "null_rows_dropped": int(null_rows),
    "duplicates_dropped": int(dupes),
    "chunk_id_mismatches": int(n_mismatched),
    "chunk_id_mismatch_rate": round(n_mismatched / len(qa), 4) if len(qa) else None,
    "rows_usable_for_eval": len(qa_eval_ready),
    "mismatch_examples": mismatched_examples,
    "question_type_breakdown": qa["question_type"].value_counts().to_dict(),
}

with open("results/statutes_qa_cleaning_report.json", "w") as f:
    json.dump(report, f, indent=2, default=str)

print(json.dumps(report, indent=2, default=str))
