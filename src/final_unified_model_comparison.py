"""Unified original-e8 vs combined-e5 comparison on two held-out sources.

Same act-aware cascade as src/end_to_end_pipeline.py (v2 / combined-e5 runs).
Sources: GSMS-B val (never used in training) and clean GovIntel e2e (exact
duplicates of combined-e5 GovIntel train pairs removed).
"""
import json
import os
import sys

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")

import pandas as pd
from sentence_transformers import SentenceTransformer

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from end_to_end_pipeline import NEW_CODE_ACTS, cascade_search_act_aware

gsms_val = pd.read_json("data/splits/val.jsonl", lines=True)
gsms_val["source"] = "GSMS-B_val"
gsms_val["true_route"] = "BNS"

with open("data/clean/e2e_test_cases.json") as f:
    e2e_cases = json.load(f)
govintel_train = pd.read_json("data/clean/govintel_extracted_v2.jsonl", lines=True)
train_questions = set(govintel_train["question"])
clean_govintel = [c for c in e2e_cases if c["question"] not in train_questions]
govintel_df = pd.DataFrame(clean_govintel)
govintel_df["source"] = "GovIntel_clean"

print(f"GSMS-B val (BNS/BNSS/BSA): {len(gsms_val)}")
print(f"Clean GovIntel (IPC+BNS): {len(govintel_df)}")
print(
    f"  IPC: {(govintel_df['true_route']=='IPC').sum()}, "
    f"BNS: {(govintel_df['true_route']=='BNS').sum()}"
)

statutes = pd.read_json("data/clean/statutes.jsonl", lines=True)
ipc_corpus = pd.read_json("data/clean/ipc_statutes.jsonl", lines=True)

bns_chunk_ids = statutes["chunk_id"].tolist()
bns_section_numbers = statutes["section_number"].astype(str).str.strip().tolist()
ipc_chunk_ids = ipc_corpus["chunk_id"].tolist()
ipc_section_numbers = ipc_corpus["ipc_section"].astype(str).str.strip().tolist()


def _mean(xs):
    return float(sum(xs) / len(xs)) if xs else None


def run_model(model_path, label):
    model = SentenceTransformer(model_path)
    print(f"\nEncoding corpora with {label}...")
    bns_emb = model.encode(statutes["text"].tolist(), show_progress_bar=True)
    ipc_emb = model.encode(ipc_corpus["text"].tolist(), show_progress_bar=True)

    results = []
    for _, row in gsms_val.iterrows():
        retrieved = cascade_search_act_aware(
            row["question"], bns_chunk_ids, bns_section_numbers, bns_emb, model, NEW_CODE_ACTS, k=5
        )
        results.append({
            "source": "GSMS-B_val",
            "route": "BNS",
            "hit": row["chunk_id"] in retrieved,
        })
    for _, row in govintel_df.iterrows():
        if row["true_route"] == "IPC":
            retrieved = cascade_search_act_aware(
                row["question"], ipc_chunk_ids, ipc_section_numbers, ipc_emb, model, {"IPC"}, k=5
            )
        else:
            retrieved = cascade_search_act_aware(
                row["question"], bns_chunk_ids, bns_section_numbers, bns_emb, model, NEW_CODE_ACTS, k=5
            )
        results.append({
            "source": "GovIntel_clean",
            "route": row["true_route"],
            "hit": row["gold_chunk_id"] in retrieved,
        })

    df = pd.DataFrame(results)
    by_source = {k: float(v) for k, v in df.groupby("source")["hit"].mean().to_dict().items()}
    by_source_n = df.groupby("source").size().to_dict()
    by_cell = {}
    for (source, route), g in df.groupby(["source", "route"]):
        by_cell[f"{source}|{route}"] = {"n": int(len(g)), "recall_at_5": float(g["hit"].mean())}

    return {
        "label": label,
        "n": len(df),
        "overall_recall_at_5": float(df["hit"].mean()),
        "by_source": by_source,
        "by_source_n": {k: int(v) for k, v in by_source_n.items()},
        "by_source_route": by_cell,
    }


if __name__ == "__main__":
    result_e8 = run_model("models/finetuned-bge-small-ipc-bns-e8", "original-e8")
    result_combined = run_model("models/finetuned-bge-small-combined-e5", "combined-e5")

    print("\n=== FINAL UNIFIED COMPARISON ===")
    print(
        f"Total n = {result_e8['n']} "
        f"({len(gsms_val)} GSMS-B val + {len(govintel_df)} clean GovIntel)"
    )
    print(f"\noriginal-e8:   overall={result_e8['overall_recall_at_5']:.1%}  by_source={result_e8['by_source']}")
    print(f"combined-e5:   overall={result_combined['overall_recall_at_5']:.1%}  by_source={result_combined['by_source']}")
    print("\nBy source × route:")
    for key in sorted(result_e8["by_source_route"]):
        e8c = result_e8["by_source_route"][key]
        c5c = result_combined["by_source_route"][key]
        print(
            f"  {key} n={e8c['n']}: "
            f"e8={e8c['recall_at_5']:.1%}  combined-e5={c5c['recall_at_5']:.1%}"
        )

    with open("results/final_unified_model_comparison.json", "w") as f:
        json.dump({
            "e8": {
                "overall": result_e8["overall_recall_at_5"],
                "by_source": result_e8["by_source"],
                "by_source_route": result_e8["by_source_route"],
            },
            "combined_e5": {
                "overall": result_combined["overall_recall_at_5"],
                "by_source": result_combined["by_source"],
                "by_source_route": result_combined["by_source_route"],
            },
            "n_total": result_e8["n"],
            "n_gsms_val": len(gsms_val),
            "n_govintel_clean": len(govintel_df),
            "n_govintel_clean_ipc": int((govintel_df["true_route"] == "IPC").sum()),
            "n_govintel_clean_bns": int((govintel_df["true_route"] == "BNS").sum()),
            "note": (
                "Act-aware cascade identical to end_to_end_pipeline.py. "
                "GSMS-B val was not used in either model's training. "
                "GovIntel_clean excludes exact question duplicates of "
                "govintel_extracted_v2.jsonl (combined-e5 train). "
                "Clean GovIntel BNS n is very small."
            ),
        }, f, indent=2)
