"""Stage 4 rule-only verifier via Ollama 14B v2 — tighter prompt + few-shot.

Same v2 prompt as src/stage4_verify_ruleonly_claude_v2.py, but uses local
qwen2.5:14b-instruct instead of the Claude API.

Output: results/stage4_verifier_14b_v2.json
"""
import argparse
import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage4_generate import OLLAMA_URL, check_ollama
from stage4_verify import KNOWN_MISMATCH_CASES, parse_irac
from stage4_verify_ruleonly import parse_ruleonly_verdict, score

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SAMPLE_PATH = RESULTS / "stage4_larger_sample.json"
OUT_PATH = RESULTS / "stage4_verifier_14b_v2.json"
MODEL = "qwen2.5:14b-instruct"

FEW_SHOT_EXAMPLES = """Here are examples of correct judgments:

---
Example 1 (NOT_SUPPORTED - Rule contradicts Conclusion):
Rule: "Nothing in this section, section 478 or section 480, shall be deemed
to require the release of any person liable to be detained for some matter
other than that in respect of which the bond or bail bond was executed."
Conclusion: "The police cannot investigate the new evidence as the case has
already been deemed closed upon filing their final report with the court."
Judgment: NOT_SUPPORTED - The Rule quoted has nothing to do with whether a
case is "closed" after a report is filed; it concerns detention for
unrelated matters. The Conclusion's claim about the case being closed is
not addressed or supported by this Rule text at all.
---
Example 2 (SUPPORTED - Rule directly supports Conclusion):
Rule: "Every police officer making an investigation under this Chapter
shall day by day enter his proceedings in the investigation in a diary..."
Conclusion: "Police officers are required to keep a daily log of their
investigation activities as per the rule provided in the statutory text."
Judgment: SUPPORTED - The Conclusion directly restates what the Rule says,
with no added claims beyond the Rule's plain text.
---
Example 3 (SUPPORTED - Conclusion reasonably restates Rule even if not
verbatim, and does not need to enumerate every element to be supported):
Rule: "A confession is irrelevant if it appears to the Court that the
making of the confession was caused by any inducement, threat, coercion or
promise having reference to the charge... proceeding from a person in
authority and sufficient to give the accused person grounds..."
Conclusion: "A confession is deemed irrelevant if caused by inducement,
threat, coercion, or promise from authority sufficient to influence the
accused."
Judgment: SUPPORTED - This is a faithful, if compressed, restatement of the
Rule. Do NOT flag a Conclusion as NOT_SUPPORTED merely because it
summarizes or omits minor secondary details from the Rule - only flag it
if it states something the Rule text does not support or actively
contradicts.
---
Example 4 (SUPPORTED - citation label not in Rule text is not a defect):
Rule: "Whenever a riot is committed for the benefit of any person who is
the owner or occupier of any land... the agent or manager of such person
shall be punishable with fine, if such agent... shall not... use all
lawful means... to prevent such assembly or riot."
Conclusion: "The law governing the agent's liability for a riot occurring
on August 10, 2024, would be governed by Section 193 of BNS 2023."
Judgment: SUPPORTED - The substantive claim (an agent's liability for
failing to prevent a riot committed for a landowner's benefit) is exactly
what the Rule establishes. The Rule text does not itself state its own
section number, but that is not a defect in the Conclusion - do not flag
citation labels that are absent from the Rule snippet as unsupported.
---
"""


def verify_rule_only_14b_v2(rule_text, conclusion_text, model=MODEL, timeout=600):
    prompt = f"""You are a strict legal fact-checker. You will be given a statutory
Rule and a Conclusion someone reached. Do NOT assume the Conclusion's
reasoning is correct. Independently determine whether the Rule, read on
its own, actually supports the Conclusion.

IMPORTANT CRITERIA:
- Only judge NOT_SUPPORTED if the Conclusion states something the Rule
  text does NOT address at all, or something the Rule text actively
  contradicts.
- Do NOT judge NOT_SUPPORTED merely because the Conclusion is a shortened,
  paraphrased, or partial restatement of the Rule - compression and
  summarization are expected and acceptable.
- Do NOT flag NOT_SUPPORTED because the Conclusion mentions a section
  number, act name, or citation label that does not literally appear in
  the Rule text. The Rule snippet is often provided without its own
  section header. Judge only the SUBSTANTIVE legal claim in the
  Conclusion - who is liable, under what conditions, and what the
  consequence is - against what the Rule text establishes. Citation
  labels are not something this check should evaluate.
- Focus specifically on: does the Conclusion's core claim (yes/no,
  who/what/when) match what the Rule actually establishes?

{FEW_SHOT_EXAMPLES}

Now judge this case:

Rule: {rule_text}

Conclusion someone reached: {conclusion_text}

Answer with exactly one word first - either SUPPORTED or NOT_SUPPORTED -
followed by one sentence of explanation."""

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


def main():
    parser = argparse.ArgumentParser(
        description="Stage 4 rule-only verifier (14B v2, few-shot)"
    )
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--output", type=Path, default=OUT_PATH)
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()

    check_ollama(args.model)
    out_path = args.output if args.output.is_absolute() else ROOT / args.output

    with SAMPLE_PATH.open() as f:
        cases = json.load(f)

    print(f"Model: {args.model} (v2 prompt + few-shot)")
    print(f"Loaded {len(cases)} cases from {SAMPLE_PATH}")
    print(f"Known mismatches: {sorted(KNOWN_MISMATCH_CASES)}")

    results = []
    for case in cases:
        parts = parse_irac(case["generated_irac"])
        if not parts["rule"] or not parts["conclusion"]:
            print(f"  skip case {case['case_number']}: missing Rule or Conclusion")
            continue
        verdict, explanation = verify_rule_only_14b_v2(
            parts["rule"],
            parts["conclusion"],
            model=args.model,
            timeout=args.timeout,
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
                    "prompt_version": "v2_few_shot",
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

    print(f"\n14B v2 (tighter prompt + few-shot) Rule-only verifier:")
    print(f"  TP={tp}/{n_known}  FP={fp}  FN={fn}  TN={tn}")
    print(f"  Precision={precision:.3f}  Recall={recall:.3f}")

    print(f"\nFull comparison:")
    print(f"  14B v1 (no few-shot):    Precision=0.200  Recall=1.000")
    print(f"  14B v2 (few-shot):       Precision={precision:.3f}  Recall={recall:.3f}")
    print(f"  Claude v2 (few-shot):    Precision=0.385  Recall=1.000")

    fps = [
        r["case_number"]
        for r in results
        if r["verdict"] == "NOT_SUPPORTED" and not r["known_mismatch"]
    ]
    fns = [
        r["case_number"]
        for r in results
        if r["verdict"] == "SUPPORTED" and r["known_mismatch"]
    ]
    if fps:
        print(f"\nFalse positives ({len(fps)}): {fps}")
    if fns:
        print(f"False negatives ({len(fns)}): {fns}")

    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
