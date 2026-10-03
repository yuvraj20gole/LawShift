"""Head-to-head temporal routing on GovIntel's held-out eval.jsonl.

eval.jsonl was never used in this project (train.jsonl only). Same date +
routing-language filter as the original 539-question Stage 1 set, applied
here to the eval split. Stage 1/2 = v2 extract_offense_date + 1 July 2024 cutoff.

Gold is what GovIntel's own assistant reply says the correct act is.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stage1_entity_extraction import extract_offense_date, route  # noqa: E402

DATE_PATTERN = re.compile(
    r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b|'
    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
    re.IGNORECASE
)
ROUTING_PATTERN = re.compile(
    r'\b(IPC|BNS)\b.{0,100}\b(applies|governs|applicable)\b',
    re.IGNORECASE,
)
FIRST_ACT_PATTERN = re.compile(r'\b(IPC|BNS)\b', re.IGNORECASE)

CUTOFF = date(2024, 7, 1)


def main():
    path = hf_hub_download(
        "aashnasharma/govintel-legal-dataset",
        "data/eval.jsonl",
        repo_type="dataset",
    )
    with open(path) as f:
        eval_lines = [json.loads(l) for l in f]

    print(f"Total GovIntel eval.jsonl rows: {len(eval_lines)}")

    results = []
    n_skipped_no_messages = 0
    n_skipped_filter = 0
    n_skipped_no_gt_act = 0

    for record in eval_lines:
        messages = record.get("messages", [])
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
        assistant_msg = next((m["content"] for m in messages if m["role"] == "assistant"), None)
        if not user_msg or not assistant_msg:
            n_skipped_no_messages += 1
            continue
        routing_match = ROUTING_PATTERN.search(assistant_msg)
        if not (DATE_PATTERN.search(user_msg) and routing_match):
            n_skipped_filter += 1
            continue

        gt_act_match = FIRST_ACT_PATTERN.search(assistant_msg)
        if not gt_act_match:
            n_skipped_no_gt_act += 1
            continue
        gt_act = gt_act_match.group(1).upper()
        routing_phrase_act = routing_match.group(1).upper()

        our_date, matched_text, reason = extract_offense_date(user_msg)
        our_route = route(our_date)

        results.append({
            "question": user_msg[:200],
            "question_full": user_msg,
            "assistant_preview": assistant_msg[:500],
            "govintel_stated_answer": gt_act,
            "govintel_routing_phrase_act": routing_phrase_act,
            "gold_sources_agree": gt_act == routing_phrase_act,
            "our_extracted_date": str(our_date),
            "our_matched_text": matched_text,
            "extract_reason": reason,
            "our_route": our_route,
            "match": our_route == gt_act,
            "match_vs_routing_phrase": our_route == routing_phrase_act,
        })

    n_total = len(results)
    n_clarify = sum(1 for r in results if r["our_route"] == "CLARIFY")
    scoreable = [r for r in results if r["our_route"] != "CLARIFY"]
    n_scoreable = len(scoreable)
    n_correct = sum(r["match"] for r in scoreable)
    accuracy = n_correct / n_scoreable if scoreable else 0.0
    n_gold_disagree = sum(1 for r in results if not r["gold_sources_agree"])
    n_correct_phrase = sum(r["match_vs_routing_phrase"] for r in scoreable)
    accuracy_phrase = n_correct_phrase / n_scoreable if scoreable else 0.0

    print(f"\nEval-set temporal-routing cases found: {n_total}")
    print(f"Our pipeline abstained (CLARIFY): {n_clarify}")
    print(
        f"Our routing accuracy on GovIntel's own eval split "
        f"(n={n_scoreable}): {accuracy:.1%}"
    )
    print(
        f"Accuracy vs routing-phrase gold (IPC/BNS ... applies/governs): "
        f"{accuracy_phrase:.1%}  "
        f"(first-act vs phrase disagree on {n_gold_disagree} cases)"
    )

    mismatches = [r for r in scoreable if not r["match"]]
    # Naive first \b(IPC|BNS)\b often hits "before the BNS came into force"
    # while the assistant's actual conclusion is IPC. Flag those.
    ipc_conclusion = re.compile(
        r'(Indian Penal Code.{0,80}\b(applies|governs)\b|'
        r'\bIPC\b.{0,40}\b(applies|governs)\b|'
        r'should be (prosecuted|charged) under the Indian Penal Code|'
        r'Therefore, IPC\b|'
        r'The Indian Penal Code 1860 applies)',
        re.IGNORECASE,
    )
    bns_conclusion = re.compile(
        r'(Bharatiya Nyaya Sanhita.{0,80}\b(applies|governs)\b|'
        r'\bBNS\b.{0,40}\b(applies|governs)\b|'
        r'should be (prosecuted|charged) under the BNS|'
        r'Therefore, BNS\b|'
        r'The charge is governed by the Bharatiya Nyaya Sanhita)',
        re.IGNORECASE,
    )
    n_gold_noise = 0
    n_real_disagree = 0
    for r in mismatches:
        preview = r.get("assistant_preview") or ""
        if r["our_route"] == "IPC" and ipc_conclusion.search(preview) and r["govintel_stated_answer"] == "BNS":
            r["mismatch_kind"] = "gold_noise_first_act_hit_BNS_mention"
            n_gold_noise += 1
        elif r["our_route"] == "BNS" and bns_conclusion.search(preview) and r["govintel_stated_answer"] == "IPC":
            r["mismatch_kind"] = "gold_noise_first_act_hit_IPC_mention"
            n_gold_noise += 1
        else:
            r["mismatch_kind"] = "real_or_ambiguous_disagreement"
            n_real_disagree += 1
    n_agree_after_noise = n_correct + n_gold_noise
    accuracy_after_noise = n_agree_after_noise / n_scoreable if scoreable else 0.0
    print(
        f"Of {len(mismatches)} first-act mismatches: "
        f"{n_gold_noise} look like gold-extraction noise "
        f"(assistant conclusion agrees with us), "
        f"{n_real_disagree} are real/ambiguous disagreements."
    )
    print(
        f"Accuracy if those gold-noise cases are counted as matches: "
        f"{accuracy_after_noise:.1%} ({n_agree_after_noise}/{n_scoreable})"
    )

    print(f"\nMismatches vs first-act gold ({len(mismatches)}):")
    for m in mismatches[:10]:
        slim = {
            "question": m["question"],
            "govintel_stated_answer": m["govintel_stated_answer"],
            "govintel_routing_phrase_act": m["govintel_routing_phrase_act"],
            "our_extracted_date": m["our_extracted_date"],
            "our_route": m["our_route"],
            "extract_reason": m["extract_reason"],
            "match": m["match"],
        }
        print(json.dumps(slim, indent=2))

    out = {
        "n_eval_rows": len(eval_lines),
        "n_skipped_no_messages": n_skipped_no_messages,
        "n_skipped_filter": n_skipped_filter,
        "n_skipped_no_gt_act": n_skipped_no_gt_act,
        "n_total": n_total,
        "n_clarify": n_clarify,
        "n_scoreable": n_scoreable,
        "n_correct": n_correct,
        "accuracy": accuracy,
        "n_gold_first_act_vs_phrase_disagree": n_gold_disagree,
        "n_correct_vs_routing_phrase": n_correct_phrase,
        "accuracy_vs_routing_phrase": accuracy_phrase,
        "n_mismatch_first_act": len(mismatches),
        "n_mismatch_gold_noise": n_gold_noise,
        "n_mismatch_real_or_ambiguous": n_real_disagree,
        "accuracy_counting_gold_noise_as_match": accuracy_after_noise,
        "cutoff": str(CUTOFF),
        "note": (
            "eval.jsonl never used in this project. Filter matches "
            "extract_stage1_real_test_cases.py (date in user question + "
            "IPC/BNS applies|governs|applicable in assistant). "
            "govintel_stated_answer = first IPC/BNS mention in assistant "
            "(protocol as specified). govintel_routing_phrase_act = the act "
            "in the applies/governs/applicable clause. Stage 1 = v2 "
            "extract_offense_date; Stage 2 = IPC if date < 2024-07-01 else BNS."
        ),
        "results": results,
    }
    out_path = ROOT / "results" / "govintel_eval_split_headtohead.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
