"""Stage 4 verifier ablations on the same 40 hand-labeled cases.

Test 1: cheap deterministic polarity check (no model).
Test 2: same verify_consistency() prompt with qwen2.5:14b-instruct.

Reads parsed Rule/Application/Conclusion from results/stage4_verifier_eval.json.
Writes results/stage4_verifier_ablation.json.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage4_generate import check_ollama
from stage4_verify import (
    KNOWN_MISMATCH_CASES,
    MODEL as MODEL_3B,
    score,
    verify_consistency,
)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PREV_EVAL = RESULTS / "stage4_verifier_eval.json"
OUT_PATH = RESULTS / "stage4_verifier_ablation.json"

MODEL_14B = "qwen2.5:14b-instruct"

NEGATION_PATTERNS = re.compile(
    r"\b(no|not|cannot|does not|is not|are not|shall not|without|never)\b",
    re.IGNORECASE,
)


def get_polarity(text):
    # crude but fast: does the sentence contain a negation word near the start?
    first_clause = text.strip().split(".")[0]
    return "negative" if NEGATION_PATTERNS.search(first_clause) else "affirmative"


def polarity_mismatch_check(application_text, conclusion_text):
    app_polarity = get_polarity(
        application_text.split(".")[-2] if "." in application_text else application_text
    )
    concl_polarity = get_polarity(conclusion_text)
    return app_polarity != concl_polarity, app_polarity, concl_polarity


def print_score(title, rows, verdict_key):
    n_known = len(KNOWN_MISMATCH_CASES)
    mapped = [
        {
            "verifier_verdict": r[verdict_key],
            "known_mismatch": r["known_mismatch"],
        }
        for r in rows
    ]
    tp, fp, fn, tn = score(mapped)
    print(f"\n{title}")
    print(f"  Correctly caught real mismatches (TP): {tp} / {n_known}")
    print(f"  Wrongly flagged consistent cases (FP): {fp}")
    print(f"  Missed real mismatches (FN): {fn}")
    print(f"  Correctly passed consistent cases (TN): {tn}")
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / n_known if n_known else 0.0
    print(f"  Precision: {prec:.3f}   Recall: {rec:.3f}")

    print(f"\n  Per-case detail on the {n_known} known mismatches:")
    for r in rows:
        if r["known_mismatch"]:
            extra = r.get("note", "")
            print(
                f"    Case {r['case_number']}: {r[verdict_key]}"
                + (f"  {extra}" if extra else "")
            )
    fps = [r for r in rows if r[verdict_key] == "MISMATCH" and not r["known_mismatch"]]
    if fps:
        print(f"\n  False positives ({len(fps)}): {[r['case_number'] for r in fps]}")
    fns = [r for r in rows if r[verdict_key] == "MATCH" and r["known_mismatch"]]
    if fns:
        print(f"  False negatives ({len(fns)}): {[r['case_number'] for r in fns]}")
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": prec, "recall": rec}


def run_polarity(prev_results):
    rows = []
    for r in prev_results:
        flagged, app_p, conc_p = polarity_mismatch_check(
            r["parsed_application"], r["parsed_conclusion"]
        )
        verdict = "MISMATCH" if flagged else "MATCH"
        note = f"app={app_p} concl={conc_p}"
        rows.append(
            {
                "case_number": r["case_number"],
                "known_mismatch": r["known_mismatch"],
                "polarity_verdict": verdict,
                "application_polarity": app_p,
                "conclusion_polarity": conc_p,
                "note": note,
            }
        )
    metrics = print_score(
        "Test 1 — polarity check (no model) against 40 hand-labeled cases:",
        rows,
        "polarity_verdict",
    )
    return rows, metrics


def run_14b(prev_results):
    check_ollama(MODEL_14B)
    rows = []
    n = len(prev_results)
    for i, r in enumerate(prev_results, start=1):
        print(
            f"  verifying {i}/{n}  case {r['case_number']} with {MODEL_14B}...",
            flush=True,
        )
        verdict, explanation = verify_consistency(
            r["parsed_rule"],
            r["parsed_application"],
            r["parsed_conclusion"],
            model=MODEL_14B,
            timeout=600,
        )
        gold = r["known_mismatch"]
        ok = (verdict == "MISMATCH") == gold
        print(
            f"    -> {verdict}  gold={'MISMATCH' if gold else 'MATCH'}  "
            f"[{'ok' if ok else 'WRONG'}]",
            flush=True,
        )
        rows.append(
            {
                "case_number": r["case_number"],
                "known_mismatch": gold,
                "verifier_verdict": verdict,
                "verifier_explanation": explanation,
                "note": explanation.replace("\n", " ")[:160],
            }
        )
        payload = json.loads(OUT_PATH.read_text()) if OUT_PATH.exists() else {}
        payload["model_14b"] = {
            "n_scored": len(rows),
            "results": rows,
        }
        with OUT_PATH.open("w") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    metrics = print_score(
        f"Test 2 — {MODEL_14B} (same prompt as 3B) against 40 hand-labeled cases:",
        rows,
        "verifier_verdict",
    )
    return rows, metrics


def main():
    with PREV_EVAL.open() as f:
        prev = json.load(f)
    prev_results = prev["results"]
    print(f"Loaded {len(prev_results)} parsed cases from {PREV_EVAL}")
    print(f"Known mismatches: {sorted(KNOWN_MISMATCH_CASES)}")
    print(
        f"3B baseline from prior run: TP={prev['tp']} FP={prev['fp']} "
        f"FN={prev['fn']} TN={prev['tn']}"
    )

    polarity_rows, polarity_metrics = run_polarity(prev_results)
    out = {
        "known_mismatch_cases": sorted(KNOWN_MISMATCH_CASES),
        "baseline_3b": {
            "model": MODEL_3B,
            "tp": prev["tp"],
            "fp": prev["fp"],
            "fn": prev["fn"],
            "tn": prev["tn"],
            "precision": prev["tp"] / (prev["tp"] + prev["fp"])
            if (prev["tp"] + prev["fp"])
            else 0.0,
            "recall": prev["tp"] / len(KNOWN_MISMATCH_CASES),
        },
        "polarity": {**polarity_metrics, "results": polarity_rows},
    }
    with OUT_PATH.open("w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    model_14b_rows, model_14b_metrics = run_14b(prev_results)
    out["model_14b"] = {**model_14b_metrics, "model": MODEL_14B, "results": model_14b_rows}

    b3 = out["baseline_3b"]
    b14 = out["model_14b"]
    print("\n=== Comparison ===")
    print(
        f"  3B:  TP {b3['tp']}/5  FP {b3['fp']}  "
        f"P={b3['precision']:.3f}  R={b3['recall']:.3f}"
    )
    print(
        f"  polarity: TP {polarity_metrics['tp']}/5  FP {polarity_metrics['fp']}  "
        f"P={polarity_metrics['precision']:.3f}  R={polarity_metrics['recall']:.3f}"
    )
    print(
        f"  14B: TP {b14['tp']}/5  FP {b14['fp']}  "
        f"P={b14['precision']:.3f}  R={b14['recall']:.3f}"
    )

    with OUT_PATH.open("w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
