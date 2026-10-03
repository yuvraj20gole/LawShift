"""Stage 4 Rule–Application–Conclusion consistency verifier.

Uses the same Qwen2.5-3B-Instruct model as generation. Only checks internal
contradiction (does the Conclusion follow from the Rule and Application).
Does not judge legal correctness against the statute.

Eval: 40 gold-chunk cases from results/stage4_larger_sample.json, scored
against the hand labels in KNOWN_MISMATCH_CASES.

Output: results/stage4_verifier_eval.json
"""
import json
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage4_generate import MODEL, OLLAMA_URL, check_ollama

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

SAMPLE_PATH = RESULTS / "stage4_larger_sample.json"
OUT_PATH = RESULTS / "stage4_verifier_eval.json"

# Hand labels from the Stage 4 review. Everything else is treated as consistent
# for this eval (user: 5 mismatches, 31 consistent; remaining cases were
# fabricated/other and still count as negatives for the mismatch detector).
KNOWN_MISMATCH_CASES = {6, 9, 12, 13, 39}


def parse_irac(generated_text: str) -> dict:
    parts = {}
    for field in ["Issue", "Rule", "Application", "Conclusion"]:
        pattern = rf"{field}:\s*(.+?)(?=\n(?:Issue|Rule|Application|Conclusion):|$)"
        m = re.search(pattern, generated_text, re.DOTALL)
        parts[field.lower()] = m.group(1).strip() if m else ""
    return parts


def parse_verdict(text: str) -> str:
    """First token MATCH/MISMATCH; otherwise first whole-word hit; else MATCH."""
    cleaned = re.sub(r"^[\s*`#\-:>]+", "", text or "").strip()
    first = re.match(r"([A-Za-z]+)", cleaned)
    token = first.group(1).upper() if first else ""
    if token == "MISMATCH":
        return "MISMATCH"
    if token == "MATCH":
        return "MATCH"
    hit = re.search(r"\b(MISMATCH|MATCH)\b", cleaned.upper())
    return hit.group(1) if hit else "MATCH"


def verify_consistency(rule_text, application_text, conclusion_text, model=MODEL, timeout=180):
    prompt = f"""You are a strict logical consistency checker. You will be given
three parts of a legal analysis: a Rule, an Application, and a Conclusion.

Your ONLY job is to check whether the Conclusion logically follows from the
Rule and Application. Do NOT evaluate whether the legal reasoning is correct
in a broader sense - only check for internal contradiction.

Rule: {rule_text}

Application: {application_text}

Conclusion: {conclusion_text}

Does the Conclusion contradict, ignore, or fail to follow from the Rule and
Application above? Answer with exactly one word first - either MATCH or
MISMATCH - followed by one sentence explaining why.

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
    return parse_verdict(text), text


def score(verifier_results):
    tp = sum(
        1
        for r in verifier_results
        if r["verifier_verdict"] == "MISMATCH" and r["known_mismatch"]
    )
    fp = sum(
        1
        for r in verifier_results
        if r["verifier_verdict"] == "MISMATCH" and not r["known_mismatch"]
    )
    fn = sum(
        1
        for r in verifier_results
        if r["verifier_verdict"] == "MATCH" and r["known_mismatch"]
    )
    tn = sum(
        1
        for r in verifier_results
        if r["verifier_verdict"] == "MATCH" and not r["known_mismatch"]
    )
    return tp, fp, fn, tn


def save(payload):
    RESULTS.mkdir(exist_ok=True)
    with OUT_PATH.open("w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def main():
    check_ollama()
    with SAMPLE_PATH.open() as f:
        cases = json.load(f)

    print(f"Loaded {len(cases)} cases from {SAMPLE_PATH}")
    print(f"Known mismatches: {sorted(KNOWN_MISMATCH_CASES)}")

    verifier_results = []
    skipped = []
    for i, case in enumerate(cases, start=1):
        parts = parse_irac(case["generated_irac"])
        if not parts["rule"] or not parts["conclusion"]:
            skipped.append(case["case_number"])
            print(
                f"  skip case {case['case_number']}: missing Rule or Conclusion",
                flush=True,
            )
            continue
        print(
            f"  verifying {i}/{len(cases)}  case {case['case_number']} "
            f"({case.get('question_type', '')})...",
            flush=True,
        )
        verdict, explanation = verify_consistency(
            parts["rule"], parts["application"], parts["conclusion"]
        )
        gold = case["case_number"] in KNOWN_MISMATCH_CASES
        ok = (verdict == "MISMATCH") == gold
        mark = "ok" if ok else "WRONG"
        print(
            f"    -> {verdict}  gold={'MISMATCH' if gold else 'MATCH'}  [{mark}]",
            flush=True,
        )
        verifier_results.append(
            {
                "case_number": case["case_number"],
                "question_type": case.get("question_type"),
                "chunk_id": case.get("chunk_id"),
                "parsed_rule": parts["rule"],
                "parsed_application": parts["application"],
                "parsed_conclusion": parts["conclusion"],
                "verifier_verdict": verdict,
                "verifier_explanation": explanation,
                "known_mismatch": gold,
            }
        )
        tp, fp, fn, tn = score(verifier_results)
        save(
            {
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "tn": tn,
                "n_scored": len(verifier_results),
                "skipped": skipped,
                "known_mismatch_cases": sorted(KNOWN_MISMATCH_CASES),
                "results": verifier_results,
            }
        )

    tp, fp, fn, tn = score(verifier_results)
    print(f"\nVerifier performance against {len(verifier_results)} hand-labeled cases:")
    print(f"  Correctly caught real mismatches (TP): {tp} / {len(KNOWN_MISMATCH_CASES)}")
    print(f"  Wrongly flagged consistent cases (FP): {fp}")
    print(f"  Missed real mismatches (FN): {fn}")
    print(f"  Correctly passed consistent cases (TN): {tn}")
    if skipped:
        print(f"  Skipped (unparseable IRAC): {skipped}")

    print(f"\nPer-case detail on the {len(KNOWN_MISMATCH_CASES)} known mismatches:")
    for r in verifier_results:
        if r["known_mismatch"]:
            expl = r["verifier_explanation"].replace("\n", " ")[:180]
            print(f"  Case {r['case_number']}: verifier said {r['verifier_verdict']} - {expl}")

    fps = [r for r in verifier_results if r["verifier_verdict"] == "MISMATCH" and not r["known_mismatch"]]
    fns = [r for r in verifier_results if r["verifier_verdict"] == "MATCH" and r["known_mismatch"]]
    if fps:
        print(f"\nFalse positives ({len(fps)}):")
        for r in fps:
            expl = r["verifier_explanation"].replace("\n", " ")[:180]
            print(f"  Case {r['case_number']}: {expl}")
    if fns:
        print(f"\nFalse negatives ({len(fns)}):")
        for r in fns:
            expl = r["verifier_explanation"].replace("\n", " ")[:180]
            print(f"  Case {r['case_number']}: {expl}")

    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
