"""Stage 4 rule-only verifier: Conclusion vs Rule, Application hidden.

Tests whether dropping Application from verifier context breaks the anchoring
problem (model no longer rubber-stamps a coherent Application→Conclusion chain).

Output defaults to results/stage4_verifier_ruleonly.json (3B).
Use --model qwen2.5:14b-instruct for the 14B ablation.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage4_generate import MODEL, OLLAMA_URL, check_ollama
from stage4_verify import KNOWN_MISMATCH_CASES, parse_irac

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SAMPLE_PATH = RESULTS / "stage4_larger_sample.json"
DEFAULT_OUT = RESULTS / "stage4_verifier_ruleonly.json"


def parse_ruleonly_verdict(text: str) -> str:
    cleaned = re.sub(r"^[\s*`#\-:>]+", "", text or "").strip()
    upper = cleaned.upper()
    if upper.startswith("NOT_SUPPORTED") or upper.startswith("NOT SUPPORTED"):
        return "NOT_SUPPORTED"
    if upper.startswith("SUPPORTED"):
        return "SUPPORTED"
    if "NOT_SUPPORTED" in upper or "NOT SUPPORTED" in upper:
        return "NOT_SUPPORTED"
    return "SUPPORTED"


def verify_rule_only(rule_text, conclusion_text, model=MODEL, timeout=180):
    prompt = f"""You are a strict legal fact-checker. You will be given a statutory
Rule and a Conclusion someone reached. Do NOT assume the Conclusion's reasoning
is correct. Independently determine whether the Rule, read on its own,
actually supports the Conclusion.

Rule: {rule_text}

Conclusion someone reached: {conclusion_text}

Based ONLY on the Rule text above - ignoring any reasoning the person may
have used - does the Rule actually support this Conclusion? Answer with
exactly one word first - either SUPPORTED or NOT_SUPPORTED - followed by
one sentence citing the specific part of the Rule that supports or
contradicts the Conclusion.

Answer:"""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "30m",
            "options": {"temperature": 0.0},
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    if "error" in payload and "response" not in payload:
        raise RuntimeError(payload["error"])
    text = payload["response"].strip()
    return parse_ruleonly_verdict(text), text


def score(results):
    tp = sum(
        1 for r in results
        if r["verdict"] == "NOT_SUPPORTED" and r["known_mismatch"]
    )
    fp = sum(
        1 for r in results
        if r["verdict"] == "NOT_SUPPORTED" and not r["known_mismatch"]
    )
    fn = sum(
        1 for r in results
        if r["verdict"] == "SUPPORTED" and r["known_mismatch"]
    )
    tn = sum(
        1 for r in results
        if r["verdict"] == "SUPPORTED" and not r["known_mismatch"]
    )
    return tp, fp, fn, tn


def main():
    parser = argparse.ArgumentParser(description="Stage 4 rule-only IRAC verifier")
    parser.add_argument("--model", default=MODEL, help="Ollama model tag")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT, help="JSON output path")
    parser.add_argument("--timeout", type=int, default=600, help="Request timeout seconds")
    args = parser.parse_args()

    check_ollama(args.model)
    out_path = args.output if args.output.is_absolute() else ROOT / args.output

    with SAMPLE_PATH.open() as f:
        cases = json.load(f)

    print(f"Model: {args.model}")
    print(f"Loaded {len(cases)} cases from {SAMPLE_PATH}")
    print(f"Known mismatches: {sorted(KNOWN_MISMATCH_CASES)}")

    results = []
    for i, case in enumerate(cases, start=1):
        parts = parse_irac(case["generated_irac"])
        if not parts["rule"] or not parts["conclusion"]:
            print(f"  skip case {case['case_number']}: missing Rule or Conclusion")
            continue
        print(
            f"  verifying {i}/{len(cases)}  case {case['case_number']} "
            f"(rule-only)...",
            flush=True,
        )
        verdict, explanation = verify_rule_only(
            parts["rule"], parts["conclusion"], model=args.model, timeout=args.timeout
        )
        gold = case["case_number"] in KNOWN_MISMATCH_CASES
        ok = (verdict == "NOT_SUPPORTED") == gold
        print(
            f"    -> {verdict}  gold={'NOT_SUPPORTED' if gold else 'SUPPORTED'}  "
            f"[{'ok' if ok else 'WRONG'}]",
            flush=True,
        )
        results.append(
            {
                "case_number": case["case_number"],
                "question_type": case.get("question_type"),
                "chunk_id": case.get("chunk_id"),
                "parsed_rule": parts["rule"],
                "parsed_conclusion": parts["conclusion"],
                "verdict": verdict,
                "explanation": explanation,
                "known_mismatch": gold,
            }
        )
        tp, fp, fn, tn = score(results)
        with out_path.open("w") as f:
            json.dump(
                {
                    "model": args.model,
                    "tp": tp,
                    "fp": fp,
                    "fn": fn,
                    "tn": tn,
                    "known_mismatch_cases": sorted(KNOWN_MISMATCH_CASES),
                    "results": results,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

    tp, fp, fn, tn = score(results)
    n_known = len(KNOWN_MISMATCH_CASES)
    print(f"\nRule-only verifier (no Application shown):")
    print(f"  TP={tp}/{n_known}  FP={fp}  FN={fn}  TN={tn}")
    print(
        f"  Precision={tp / (tp + fp) if tp + fp else 0:.3f}  "
        f"Recall={tp / n_known:.3f}"
    )
    if args.model != MODEL:
        print(
            f"\nCompare to 3B Rule-only: TP=5/5, FP=32, "
            f"Precision=0.135, Recall=1.000"
        )
    print(f"\nPer-known-mismatch detail:")
    for r in results:
        if r["known_mismatch"]:
            expl = r["explanation"].replace("\n", " ")[:150]
            print(f"  Case {r['case_number']}: {r['verdict']} - {expl}")

    fps = [r for r in results if r["verdict"] == "NOT_SUPPORTED" and not r["known_mismatch"]]
    if fps:
        print(f"\nFalse positives ({len(fps)}): {[r['case_number'] for r in fps]}")
    fns = [r for r in results if r["verdict"] == "SUPPORTED" and r["known_mismatch"]]
    if fns:
        print(f"False negatives ({len(fns)}): {[r['case_number'] for r in fns]}")

    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
