"""Stage 1 -> 2 -> 3 end-to-end pipeline on real GovIntel questions.

Stage 1: extract offense date only (v2 extractor).
Stage 2: IPC if date < 2024-07-01 else BNS.
Stage 3: cascade retrieval on the routed corpus, RAW question text unmodified.

original-e8 is in-domain on the BNS/BNSS/BSA corpus and out-of-domain on IPC.
"""
import json
import os
import re
import sys
from datetime import date

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")

import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from stage1_entity_extraction import extract_offense_date

CUTOFF = date(2024, 7, 1)

# find_citations from src/extract_govintel_v2.py (not imported: that file runs on load)
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
    found = {}
    for act, act_pat in ACT_NAMES.items():
        for m in re.finditer(rf"Sections?\s+{SEC_LIST}\s+of\s+the\s+{act_pat}", text, re.IGNORECASE):
            found.setdefault(act, set()).update(split_numbers(m.group(1)))
        for m in re.finditer(rf"{act_pat}\s*,?\s*Section\s+({SEC_NUM})", text, re.IGNORECASE):
            found.setdefault(act, set()).add(m.group(1))
    stat_m = re.search(r"Applicable statute:\s*([^\n]+)", text, re.IGNORECASE)
    sec_m = re.search(rf"Applicable section:\s*Section\s+({SEC_NUM})", text, re.IGNORECASE)
    if stat_m and sec_m:
        for act, act_pat in ACT_NAMES.items():
            if re.search(act_pat, stat_m.group(1), re.IGNORECASE):
                found.setdefault(act, set()).add(sec_m.group(1))
    return found


def find_ipc_sections(text):
    """Single-unambiguous IPC cites, matching how GovIntel actually writes them."""
    found = set()
    ipc_act = r"(?:IPC(?:\s*,?\s*1860)?|Indian\s+Penal\s+Code(?:\s*,?\s*1860)?)"
    sec = r"(\d+[A-Za-z]{0,3})"
    patterns = [
        rf"Sections?\s+{sec}\s+of\s+the\s+{ipc_act}",
        rf"{ipc_act}\s*,?\s*Section\s+{sec}",
        rf"Sections?\s+{sec}\s+of\s+the\s+IPC\b",
        rf"Sections?\s+{sec}\s+IPC\b",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            found.add(m.group(1))
    return found


def lookup_bns(act, sec, valid_bns_lookup):
    if (act, sec) in valid_bns_lookup:
        return valid_bns_lookup[(act, sec)]
    base = re.sub(r"\([^)]*\)$", "", sec).strip()
    return valid_bns_lookup.get((act, base))


def lookup_ipc(sec, valid_ipc_lookup):
    if sec in valid_ipc_lookup:
        return valid_ipc_lookup[sec]
    base = re.sub(r"\([^)]*\)$", "", sec).strip()
    return valid_ipc_lookup.get(base)


# BNSS/BSA before BNS so "BNSS 173" is not parsed as BNS + leftover "S".
ACT_NUMBER_PATTERN = re.compile(
    r'\b(IPC|BNSS|BSA|BNS)\s*(?:Section|Sec\.?|§)?\s*(\d+[A-Za-z]{0,3})\b|'
    r'\bSection\s+(\d+[A-Za-z]{0,3})\s+of\s+the\s+(?:Indian Penal Code|IPC|Bharatiya Nyaya Sanhita|BNS|Bharatiya Nagarik Suraksha Sanhita|BNSS|Bharatiya Sakshya Adhiniyam|BSA)',
    re.IGNORECASE,
)

NEW_CODE_ACTS = {"BNS", "BNSS", "BSA"}


def extract_act_scoped_numbers(query):
    """Returns {act: set(numbers)} — only numbers explicitly tied to a named act."""
    found = {}
    for m in ACT_NUMBER_PATTERN.finditer(query):
        if m.group(1):  # "IPC 201" / "BNS Section 238" style
            act, num = m.group(1).upper(), m.group(2)
        else:  # "Section 201 of the Indian Penal Code" style
            act_text = m.group(0)
            num = m.group(3)
            if re.search(r"indian penal code|\bipc\b", act_text, re.IGNORECASE):
                act = "IPC"
            elif re.search(r"bharatiya nagarik|\bbnss\b", act_text, re.IGNORECASE):
                act = "BNSS"
            elif re.search(r"bharatiya sakshya|\bbsa\b", act_text, re.IGNORECASE):
                act = "BSA"
            elif re.search(r"bharatiya nyaya sanhita|\bbns\b", act_text, re.IGNORECASE):
                act = "BNS"
            else:
                continue
        found.setdefault(act, set()).add(num)
    return found


def chunk_act(chunk_id):
    return str(chunk_id).split("_", 1)[0].upper()


def cascade_search_act_aware(query, chunk_ids, section_numbers, corpus_emb, model, corpus_acts, k=5):
    """Exact-match only numbers explicitly tied to an act in corpus_acts.

    corpus_acts: e.g. {"IPC"} or {"BNS", "BNSS", "BSA"}. A mention of IPC 201
    does not short-circuit a BNS corpus search, and BNS_148 is not added for
    a BNSS 148 mention.
    """
    results = []
    act_numbers = extract_act_scoped_numbers(query)
    for act, nums in act_numbers.items():
        if act not in corpus_acts:
            continue
        for num in nums:
            for i, sn in enumerate(section_numbers):
                if sn == num and chunk_act(chunk_ids[i]) == act:
                    if chunk_ids[i] not in results:
                        results.append(chunk_ids[i])

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


def build_ipc_corpus():
    mapping = pd.read_json("data/clean/mapping.jsonl", lines=True)
    ipc_corpus = mapping[mapping["ipc_description"].notna()][
        ["ipc_section", "ipc_heading", "ipc_description"]
    ].copy()
    ipc_corpus["chunk_id"] = "IPC_" + ipc_corpus["ipc_section"].astype(str)
    ipc_corpus["text"] = ipc_corpus["ipc_description"]
    ipc_corpus.to_json("data/clean/ipc_statutes.jsonl", orient="records", lines=True)
    print(f"IPC retrieval corpus: {len(ipc_corpus)} sections")
    return ipc_corpus


def extract_e2e_cases(ipc_corpus, bns_statutes):
    path = hf_hub_download(
        "aashnasharma/govintel-legal-dataset", "data/train.jsonl", repo_type="dataset"
    )
    with open(path) as f:
        lines = [json.loads(l) for l in f]

    valid_bns_lookup = {}
    for _, row in bns_statutes.iterrows():
        key = (row["act"].split()[0].upper(), str(row["section_number"]).strip())
        valid_bns_lookup[key] = row["chunk_id"]
    valid_ipc_lookup = {str(s): f"IPC_{s}" for s in ipc_corpus["ipc_section"].astype(str)}

    e2e_cases = []
    for record in lines:
        messages = record.get("messages", [])
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
        assistant_msg = next((m["content"] for m in messages if m["role"] == "assistant"), None)
        if not user_msg or not assistant_msg:
            continue

        extracted_date, matched_date_text, date_reason = extract_offense_date(user_msg)
        if extracted_date is None:
            continue

        true_route = "IPC" if extracted_date < CUTOFF else "BNS"

        if true_route == "BNS":
            found = find_citations(assistant_msg)
            total = sum(len(v) for v in found.values())
            if total != 1:
                continue
            act, secs = next(iter(found.items()))
            sec = next(iter(secs))
            gold_chunk = lookup_bns(act, sec, valid_bns_lookup)
        else:
            ipc_matches = find_ipc_sections(assistant_msg)
            if len(ipc_matches) != 1:
                continue
            gold_chunk = lookup_ipc(next(iter(ipc_matches)), valid_ipc_lookup)

        if gold_chunk is None:
            continue

        e2e_cases.append({
            "question": user_msg,
            "true_offense_date": str(extracted_date),
            "true_route": true_route,
            "gold_chunk_id": gold_chunk,
        })

    print(f"End-to-end test cases: {len(e2e_cases)}")
    print(f"  IPC-routed: {sum(1 for c in e2e_cases if c['true_route']=='IPC')}")
    print(f"  BNS-routed: {sum(1 for c in e2e_cases if c['true_route']=='BNS')}")
    with open("data/clean/e2e_test_cases.json", "w") as f:
        json.dump(e2e_cases, f, indent=2)
    return e2e_cases


def run_pipeline(
    e2e_cases,
    ipc_corpus,
    bns_statutes,
    model_path="models/finetuned-bge-small-ipc-bns-e8",
    out_path="results/end_to_end_pipeline_eval_v2.json",
):
    model = SentenceTransformer(model_path)
    print(f"Loaded embedding model: {model_path}")

    bns_chunk_ids = bns_statutes["chunk_id"].tolist()
    bns_section_numbers = bns_statutes["section_number"].astype(str).str.strip().tolist()
    print("Encoding BNS/BNSS/BSA corpus...")
    bns_emb = model.encode(bns_statutes["text"].tolist(), show_progress_bar=True)

    ipc_chunk_ids = ipc_corpus["chunk_id"].tolist()
    ipc_section_numbers = ipc_corpus["ipc_section"].astype(str).str.strip().tolist()
    print("Encoding IPC corpus...")
    ipc_emb = model.encode(ipc_corpus["text"].tolist(), show_progress_bar=True)

    pipeline_results = []
    for case in e2e_cases:
        stage1_date, _, _ = extract_offense_date(case["question"])
        if stage1_date is None:
            pipeline_results.append({**case, "pipeline_outcome": "CLARIFY", "correct": None})
            continue

        stage2_route = "IPC" if stage1_date < CUTOFF else "BNS"

        if stage2_route == "IPC":
            retrieved = cascade_search_act_aware(
                case["question"], ipc_chunk_ids, ipc_section_numbers, ipc_emb, model, {"IPC"}, k=5
            )
        else:
            retrieved = cascade_search_act_aware(
                case["question"], bns_chunk_ids, bns_section_numbers, bns_emb, model, NEW_CODE_ACTS, k=5
            )

        hit = case["gold_chunk_id"] in retrieved
        route_correct = stage2_route == case["true_route"]

        pipeline_results.append({
            **case,
            "stage1_extracted_date": str(stage1_date),
            "stage2_route": stage2_route,
            "route_correct": route_correct,
            "stage3_hit_at_5": hit,
            "end_to_end_correct": route_correct and hit,
        })

    n_total = len(pipeline_results)
    n_clarify = sum(1 for r in pipeline_results if r.get("pipeline_outcome") == "CLARIFY")
    scoreable = [r for r in pipeline_results if r.get("pipeline_outcome") != "CLARIFY"]

    route_acc = sum(r["route_correct"] for r in scoreable) / len(scoreable) if scoreable else None
    e2e_acc_overall = (
        sum(r["end_to_end_correct"] for r in scoreable) / len(scoreable) if scoreable else None
    )

    ipc_cases = [r for r in scoreable if r["true_route"] == "IPC"]
    bns_cases = [r for r in scoreable if r["true_route"] == "BNS"]
    e2e_acc_ipc = (
        sum(r["end_to_end_correct"] for r in ipc_cases) / len(ipc_cases) if ipc_cases else None
    )
    e2e_acc_bns = (
        sum(r["end_to_end_correct"] for r in bns_cases) / len(bns_cases) if bns_cases else None
    )
    ipc_stage3 = (
        sum(r["stage3_hit_at_5"] for r in ipc_cases) / len(ipc_cases) if ipc_cases else None
    )
    bns_stage3 = (
        sum(r["stage3_hit_at_5"] for r in bns_cases) / len(bns_cases) if bns_cases else None
    )

    print(f"Total cases: {n_total}, CLARIFY (no date found): {n_clarify}, scoreable: {len(scoreable)}")
    print(f"Stage 2 routing accuracy: {route_acc:.1%}")
    print(f"Overall E2E accuracy (act-aware fix): {e2e_acc_overall:.1%} (was 78.5%)")
    print(f"IPC subset (n={len(ipc_cases)}, e8 is OUT-OF-DOMAIN here): {e2e_acc_ipc:.1%} (was 82.0%)")
    print(f"BNS subset (n={len(bns_cases)}, e8's trained domain): {e2e_acc_bns:.1%} (was 66.7%)")
    print(f"  Stage 3 Recall@5 IPC: {ipc_stage3:.1%}")
    print(f"  Stage 3 Recall@5 BNS: {bns_stage3:.1%}")

    summary = {
        "n_total": n_total,
        "n_clarify": n_clarify,
        "n_scoreable": len(scoreable),
        "n_ipc": len(ipc_cases),
        "n_bns": len(bns_cases),
        "routing_accuracy": route_acc,
        "e2e_accuracy_overall": e2e_acc_overall,
        "e2e_accuracy_ipc_subset": e2e_acc_ipc,
        "e2e_accuracy_bns_subset": e2e_acc_bns,
        "stage3_recall_at_5_ipc": ipc_stage3,
        "stage3_recall_at_5_bns": bns_stage3,
        "model_path": model_path,
        "note": (
            "Act-aware cascade unchanged. Same 460 cases as "
            "end_to_end_pipeline_eval_v2.json. Only the embedding model differs."
        ),
        "results": pipeline_results,
    }
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    return summary


if __name__ == "__main__":
    ipc_corpus = pd.read_json("data/clean/ipc_statutes.jsonl", lines=True)
    bns_statutes = pd.read_json("data/clean/statutes.jsonl", lines=True)
    with open("data/clean/e2e_test_cases.json") as f:
        e2e_cases = json.load(f)
    print(f"Loaded {len(e2e_cases)} existing e2e cases (not rebuilt)")
    run_pipeline(
        e2e_cases,
        ipc_corpus,
        bns_statutes,
        model_path="models/finetuned-bge-small-combined-e5",
        out_path="results/end_to_end_pipeline_combined_e5.json",
    )
