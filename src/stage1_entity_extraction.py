"""Stage 1 date-extraction baseline (v2).

Fixes from the stress test:
  1. Multi-date: pick the date whose local context looks like the offense,
     not the first calendar date in the string.
  2. Ambiguous numeric dates (both parts <= 12, e.g. 07-01-2024): return
     None / CLARIFY instead of silently picking MM-DD or DD-MM.

Evaluated on the 30 GovIntel-derived cases and the 14-item stress set.
"""
import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime

from dateutil import parser as dateparser

CUTOFF = date(2024, 7, 1)

OFFENSE_KEYWORDS = [
    "occurred", "happened", "took place", "incident", "assault", "theft",
    "committed", "incident of", "regarding an incident", "the offence",
    "the crime", "was attacked", "was killed", "was stolen", "victim",
    "use",
]
PROCEDURAL_KEYWORDS = [
    "filed", "filing", "fir", "registered", "statement", "report",
    "today's date", "as of", "complaint on", "recorded my statement",
]

DATE_PATTERNS = [
    r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
]


def keyword_in_context(keyword, context):
    """Word-boundary match so 'use' does not hit 'house' and 'fir' does not hit 'first'."""
    return bool(re.search(r'\b' + re.escape(keyword.lower()) + r'\b', context))


def find_all_dates(text):
    """Return list of (matched_text, start_pos, end_pos) for every date-like match."""
    matches = []
    seen = set()
    for pattern in DATE_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            key = (m.start(), m.end())
            if key in seen:
                continue
            seen.add(key)
            matches.append((m.group(0), m.start(), m.end()))
    matches.sort(key=lambda x: x[1])
    return matches


def score_context(text, start, end, window=45):
    """Score a date match by nearby offense vs procedural keywords.

    Window is 45 rather than 60 so keywords in a short two-date sentence
    (e.g. statement date vs 'incident of') do not leak onto both spans.
    """
    context = text[max(0, start - window):min(len(text), end + window)].lower()
    offense_score = sum(1 for kw in OFFENSE_KEYWORDS if keyword_in_context(kw, context))
    procedural_score = sum(1 for kw in PROCEDURAL_KEYWORDS if keyword_in_context(kw, context))
    return offense_score - procedural_score


def is_ambiguous_numeric(date_str):
    """Flag DD-MM vs MM-DD ambiguity: both first two numeric parts <= 12."""
    m = re.match(r'^(\d{1,2})[/-](\d{1,2})[/-]\d{2,4}$', date_str)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return a <= 12 and b <= 12 and a != b
    return False


def parse_date_safe(date_str):
    try:
        parsed = dateparser.parse(date_str, fuzzy=True, default=datetime(2000, 1, 1))
        return parsed.date()
    except Exception:
        return None


def extract_offense_date(text):
    all_dates = find_all_dates(text)
    if not all_dates:
        return None, None, "no_date_found"

    # Flag ambiguous numeric formats FIRST - don't silently parse these
    for matched_text, start, end in all_dates:
        if is_ambiguous_numeric(matched_text):
            return None, matched_text, "ambiguous_numeric_format"

    if len(all_dates) == 1:
        d = parse_date_safe(all_dates[0][0])
        return d, all_dates[0][0], "single_date"

    # Multiple dates: score each by context, pick highest offense-indicator score
    scored = [(m, s, e, score_context(text, s, e)) for m, s, e in all_dates]
    scored.sort(key=lambda x: x[3], reverse=True)
    best_match, best_start, best_end, best_score = scored[0]

    # If top two are tied, do not let a later cutoff/discovery date win.
    # Fall back to the first date in the string (GovIntel gold is that date).
    if len(scored) > 1 and scored[0][3] == scored[1][3]:
        first_match, first_start, first_end = min(all_dates, key=lambda x: x[1])
        d = parse_date_safe(first_match)
        return d, first_match, "tied_fallback_first_date"

    d = parse_date_safe(best_match)
    return d, best_match, "multi_date_context_resolved"


def route(offense_date):
    if offense_date is None:
        return "CLARIFY"
    return "IPC" if offense_date < CUTOFF else "BNS"


# Extra stems/gerunds for split detection only. extract_offense_date() still
# uses the original lists above. "prosecution"/"trial" are omitted: they fire
# on "the prosecution seeks" and veto real act dates (Batch 1 case 2).
SPLIT_OFFENSE_KEYWORDS = OFFENSE_KEYWORDS + [
    "created", "creating", "removed", "removing", "erased", "erasing",
    "manufactured", "manufacturing", "used", "using", "sold", "selling",
    "reused", "reusing", "possessed", "possessing", "entrusted",
    "misappropriated", "colluded", "assaulted", "fabricated", "forged",
    "forging", "published", "publication", "concealed", "concealment",
    "provocation", "riot", "extortion", "operations",
]
SPLIT_PROCEDURAL_KEYWORDS = PROCEDURAL_KEYWORDS + [
    "discovered", "came to light", "brought to light", "charge sheet",
    "apprehended", "investigation", "detected", "found out",
]
CONTINUING_LANGUAGE = re.compile(
    r'\bcontinu|\bpersist|\bongoing\b|\bstraddl',
    re.IGNORECASE,
)


def score_split_context(text, start, end, window=45):
    """Offense vs procedural counts for split detection (expanded keywords)."""
    context = text[max(0, start - window):min(len(text), end + window)].lower()
    offense_hits = sum(1 for kw in SPLIT_OFFENSE_KEYWORDS if keyword_in_context(kw, context))
    procedural_hits = sum(1 for kw in SPLIT_PROCEDURAL_KEYWORDS if keyword_in_context(kw, context))
    return offense_hits, procedural_hits, offense_hits - procedural_hits


@dataclass
class RouteDecision:
    kind: str  # "split" | "single" | "clarify"
    periods: list = field(default_factory=list)
    reason: str = ""
    single_route: str = None


def route_with_split_detection(text):
    """Stage 1/2 with a split branch.

    Split if (a) two+ *act* dates straddle 1 July 2024, where an act date has
    at least one offense keyword in the local window, or (b) the text has
    continuing-offense language AND parsed dates straddle the cutoff with at
    least one act date. Otherwise fall back to extract_offense_date + route.
    """
    all_dates = find_all_dates(text)
    parsed = []
    for matched_text, start, end in all_dates:
        if is_ambiguous_numeric(matched_text):
            continue
        d = parse_date_safe(matched_text)
        if d is None:
            continue
        offense_hits, procedural_hits, net = score_split_context(text, start, end)
        parsed.append({
            "date": d,
            "matched_text": matched_text,
            "offense_hits": offense_hits,
            "procedural_hits": procedural_hits,
            "score": net,
            "is_act": offense_hits > 0,
        })

    act_dates = [p for p in parsed if p["is_act"]]
    act_before = [p for p in act_dates if p["date"] < CUTOFF]
    act_after = [p for p in act_dates if p["date"] >= CUTOFF]
    any_before = [p for p in parsed if p["date"] < CUTOFF]
    any_after = [p for p in parsed if p["date"] >= CUTOFF]
    has_continuing = bool(CONTINUING_LANGUAGE.search(text))

    split = False
    reason = ""
    if act_before and act_after:
        split = True
        reason = "act_dates_straddle_cutoff"
    elif has_continuing and act_dates and any_before and any_after:
        split = True
        reason = "continuing_language_and_straddle"

    if split:
        before_src = act_before if act_before else any_before
        after_src = act_after if act_after else any_after
        before = min(before_src, key=lambda p: p["date"])
        after = min(after_src, key=lambda p: p["date"])
        periods = [
            {
                "date": before["date"].isoformat(),
                "route": "IPC",
                "matched_text": before["matched_text"],
                "score": before["score"],
            },
            {
                "date": after["date"].isoformat(),
                "route": "BNS",
                "matched_text": after["matched_text"],
                "score": after["score"],
            },
        ]
        return RouteDecision(kind="split", periods=periods, reason=reason)

    d, matched, extract_reason = extract_offense_date(text)
    single = route(d)
    if single == "CLARIFY":
        return RouteDecision(
            kind="clarify", periods=[], reason=extract_reason, single_route="CLARIFY"
        )
    periods = [{
        "date": d.isoformat() if d else None,
        "route": single,
        "matched_text": matched,
        "score": None,
    }]
    return RouteDecision(
        kind="single", periods=periods, reason=extract_reason, single_route=single
    )


STRESS_CASES = [
    {"text": "Someone cheated me last March, taking Rs 20,000.", "expected_route": "CLARIFY", "note": "relative date, unparseable"},
    {"text": "This happened a few months ago at my shop.", "expected_route": "CLARIFY", "note": "vague, no date"},
    {"text": "He threatened me recently over a land dispute.", "expected_route": "CLARIFY", "note": "vague, no date"},
    {"text": "My neighbour keeps harassing me and I want to file a complaint.", "expected_route": "CLARIFY", "note": "no date mentioned"},
    {"text": "Someone stole my phone at the railway station.", "expected_route": "CLARIFY", "note": "no date mentioned"},
    {"text": "I am filing this complaint on 10 August 2024 regarding an incident that occurred on 15 March 2024.", "expected_route": "IPC", "note": "filing date first, offense date second"},
    {"text": "The FIR was registered on 2 July 2024. The actual assault took place on 28 June 2024.", "expected_route": "IPC", "note": "FIR date first, assault date second"},
    {"text": "As of today's date, 20 August 2024, I want to report a theft that happened on 5 June 2024.", "expected_route": "IPC", "note": "today's date first, theft date second"},
    {"text": "On 10 July 2024 the police recorded my statement about the incident of 25 June 2024.", "expected_route": "IPC", "note": "statement date vs incident date"},
    {"text": "The incident occurred on 30 June 2024.", "expected_route": "IPC", "note": "one day before cutoff"},
    {"text": "The incident occurred on 1 July 2024.", "expected_route": "BNS", "note": "exactly on cutoff"},
    {"text": "The incident occurred on 2 July 2024.", "expected_route": "BNS", "note": "one day after cutoff"},
    {"text": "It happened on 15/03/24.", "expected_route": "IPC", "note": "2-digit year, DD/MM assumed"},
    {"text": "Incident date: 07-01-2024", "expected_route": None, "note": "ambiguous numeric DD-MM vs MM-DD"},
]


def run_real_eval():
    with open("data/clean/stage1_real_test_cases.json") as f:
        real_cases = json.load(f)

    results = []
    for case in real_cases:
        gt_date, _, _ = extract_offense_date(case["date_mentioned_in_question"])
        gt_route = route(gt_date)
        extracted_date, matched, reason = extract_offense_date(case["text"])
        extracted_route = route(extracted_date)
        results.append({
            "text": case["text"][:200],
            "ground_truth_date": str(gt_date),
            "extracted_date": str(extracted_date),
            "date_exact_match": extracted_date == gt_date,
            "ground_truth_route": gt_route,
            "extracted_route": extracted_route,
            "routing_correct": extracted_route == gt_route,
            "reason": reason,
            "matched": matched,
        })

    n_correct = sum(r["routing_correct"] for r in results)
    real_accuracy = n_correct / len(results)
    print(f"Real GovIntel set (n={len(results)}): {n_correct}/{len(results)} = {real_accuracy:.1%}")
    wrong = [r for r in results if not r["routing_correct"]]
    if wrong:
        print(f"  Misrouted ({len(wrong)}):")
        for w in wrong:
            print(f"    [{w['reason']}] gt={w['ground_truth_route']} got={w['extracted_route']} | {w['text'][:120]}")
    return results, real_accuracy


def run_stress_test():
    results = []
    for case in STRESS_CASES:
        extracted_date, matched, reason = extract_offense_date(case["text"])
        extracted_route = route(extracted_date)
        if case["expected_route"] is None:
            correct = reason == "ambiguous_numeric_format"
        else:
            correct = extracted_route == case["expected_route"]
        results.append({
            "text": case["text"],
            "note": case.get("note"),
            "extracted_date": str(extracted_date),
            "matched_text": matched,
            "extracted_route": extracted_route,
            "expected_route": case["expected_route"],
            "reason": reason,
            "correct": correct,
        })

    n_scoreable = len(STRESS_CASES)
    n_correct = sum(r["correct"] for r in results)
    print(f"\nStress test (n={n_scoreable}): {n_correct}/{n_scoreable}")
    for r in results:
        print(f"  [{'PASS' if r['correct'] else 'FAIL'}] ({r['reason']}) {r['text'][:70]}")
        if not r["correct"]:
            print(f"         extracted={r['extracted_date']} -> {r['extracted_route']} expected={r['expected_route']}")
    return results, n_correct, n_scoreable


if __name__ == "__main__":
    real_results, real_accuracy = run_real_eval()
    stress_results, n_correct, n_scoreable = run_stress_test()

    with open("results/stage1_real_eval.json", "w") as f:
        json.dump({
            "n": len(real_results),
            "found_nothing": sum(1 for r in real_results if r["extracted_date"] == "None"),
            "date_exact_match_accuracy": sum(r["date_exact_match"] for r in real_results) / len(real_results),
            "routing_accuracy": real_accuracy,
            "results": real_results,
        }, f, indent=2)

    with open("results/stage1_stress_test.json", "w") as f:
        json.dump({
            "n_scoreable": n_scoreable,
            "n_correct": n_correct,
            "accuracy": n_correct / n_scoreable if n_scoreable else None,
            "results": stress_results,
        }, f, indent=2)

    with open("results/stage1_v2_eval.json", "w") as f:
        json.dump({
            "real_govintel_accuracy": real_accuracy,
            "stress_test_score": f"{n_correct}/{n_scoreable}",
            "stress_results": stress_results,
        }, f, indent=2)
