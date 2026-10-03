"""Stage 4 rule-only verifier via Claude (Anthropic API).

Same prompt as local Ollama rule-only runs; scores against the 40 hand-labeled
gold-chunk cases.

Output: results/stage4_verifier_claude.json
"""
import argparse
import json
import sys
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage4_verify import KNOWN_MISMATCH_CASES, parse_irac
from stage4_verify_ruleonly import parse_ruleonly_verdict, score

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SAMPLE_PATH = RESULTS / "stage4_larger_sample.json"
OUT_PATH = RESULTS / "stage4_verifier_claude.json"
DEFAULT_MODEL = "claude-sonnet-4-5"


def verify_rule_only_claude(rule_text, conclusion_text, client, model=DEFAULT_MODEL):
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
contradicts the Conclusion."""

    response = client.messages.create(
        model=model,
        max_tokens=150,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    return parse_ruleonly_verdict(text), text


def main():
    parser = argparse.ArgumentParser(description="Stage 4 rule-only verifier (Claude)")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output", type=Path, default=OUT_PATH)
    args = parser.parse_args()

    client = anthropic.Anthropic()
    out_path = args.output if args.output.is_absolute() else ROOT / args.output

    # Fail fast if the API key is missing or rejected.
    try:
        client.messages.create(
            model=args.model,
            max_tokens=5,
            messages=[{"role": "user", "content": "ping"}],
        )
    except anthropic.AuthenticationError:
        print(
            "Anthropic API authentication failed (401). "
            "Set a valid ANTHROPIC_API_KEY and retry.",
            file=sys.stderr,
        )
        raise SystemExit(1)

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
        verdict, explanation = verify_rule_only_claude(
            parts["rule"], parts["conclusion"], client, model=args.model
        )
        gold = case["case_number"] in KNOWN_MISMATCH_CASES
        ok = (verdict == "NOT_SUPPORTED") == gold
        print(
            f"Case {case['case_number']}: {verdict}  "
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
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / n_known

    print(f"\nClaude Sonnet 4.5 Rule-only verifier:")
    print(f"  TP={tp}/{n_known}  FP={fp}  FN={fn}  TN={tn}")
    print(f"  Precision={precision:.3f}  Recall={recall:.3f}")

    print(f"\nComparison so far:")
    print(f"  3B local:   TP=5/5  FP=32  Precision=0.135  Recall=1.000")
    print(f"  14B local:  TP=5/5  FP=20  Precision=0.200  Recall=1.000")
    print(
        f"  Claude:     TP={tp}/{n_known}  FP={fp}  "
        f"Precision={precision:.3f}  Recall={recall:.3f}"
    )

    fps = [r["case_number"] for r in results if r["verdict"] == "NOT_SUPPORTED" and not r["known_mismatch"]]
    fns = [r["case_number"] for r in results if r["verdict"] == "SUPPORTED" and r["known_mismatch"]]
    if fps:
        print(f"\nFalse positives ({len(fps)}): {fps}")
    if fns:
        print(f"False negatives ({len(fns)}): {fns}")

    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
