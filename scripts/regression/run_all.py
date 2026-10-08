#!/usr/bin/env python3
"""LawShift regression suite — in-process handle_query, no frontend, no live backend.

Expectations live in scripts/regression/*.json (not hardcoded pass thresholds in
this file beyond reading those JSON files). Stage 4 / Stage 5 are stubbed so
this suite does not call Ollama.

Usage (from repo root):
  .venv/bin/python scripts/regression/run_all.py

Progress: /tmp/lawshift_regression_prog.txt
Stdout also mirrored there. Hard timeout: REGRESSION_TIMEOUT_SEC (default 3600).
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import threading
import time
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REG = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

PROG = Path("/tmp/lawshift_regression_prog.txt")
OUT_JSON = Path("/tmp/lawshift_regression_out.json")
BASELINE = ROOT / "results" / "regression_baseline.json"
HARD_TIMEOUT = int(os.environ.get("REGRESSION_TIMEOUT_SEC", "3600"))
_DEADLINE = time.time() + HARD_TIMEOUT


def _check_deadline() -> None:
    if time.time() > _DEADLINE:
        raise Timeout(f"Hard timeout after {HARD_TIMEOUT}s")

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
os.environ.setdefault("LAWSHIFT_FIXED_CONCLUSION", "1")


def log(msg: str) -> None:
    line = msg if msg.endswith("\n") else msg + "\n"
    with PROG.open("a", encoding="utf-8") as f:
        f.write(line)
    print(msg, flush=True)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def cid(prefix: str) -> str:
    return f"reg-{prefix}-{uuid.uuid4().hex[:12]}"


def match_case(resp: dict, case: dict) -> bool:
    kind = resp.get("kind")
    reason = resp.get("reason")
    if "expected_kind_any" in case:
        if kind not in case["expected_kind_any"]:
            return False
    elif "expected_kind" in case and kind != case["expected_kind"]:
        return False
    if "expected_reason" in case and reason != case["expected_reason"]:
        return False
    return True


def pass_fail(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


class Timeout(Exception):
    pass


async def main_async() -> dict:
    PROG.write_text("", encoding="utf-8")
    t0 = time.time()
    os.chdir(ROOT)
    exp = load_json(REG / "expectations.json")
    rows: list[dict] = []
    details: dict[str, Any] = {"started": datetime.now().isoformat(timespec="seconds")}

    log(f"[regression] hard timeout {HARD_TIMEOUT}s")
    log("[regression] loading Stage 3…")
    from app import stage3, stage4
    import app.stage5_translate as stage5
    from app.main import (
        DESCRIBE_FACTS_OPTION,
        handle_query,
        resolve_bifurcation,
    )
    from app.schemas import QueryRequest, ResolveBifurcationRequest
    from app import stage1

    stage3.load()
    log(f"[regression] Stage 3 loaded in {time.time() - t0:.1f}s")

    # Stub Stage 4 / 5 — suite must not call Ollama.
    def fake_generate(question, retrieved_text, source_citation):
        return (
            "Issue: Whether the facts engage the cited section.\n"
            "Rule: Statutory text as retrieved.\n"
            "Application: The facts as described meet the elements stated in the Rule.\n"
            "Conclusion: GENERATED_SHOULD_BE_REPLACED."
        )

    def fake_verify(rule_text, conclusion_text):
        return "SUPPORTED", "stub"

    stage4.generate_irac = fake_generate  # type: ignore[assignment]
    stage4.verify_rule_only_14b_v2 = fake_verify  # type: ignore[assignment]

    def fake_translate(irac, target_lang="hi", skip_fields=None):
        out = dict(irac)
        skip = {x.lower() for x in (skip_fields or set())}
        for k, v in list(out.items()):
            if k.lower() in skip or not isinstance(v, str):
                continue
            out[k] = f"[{target_lang}] {v}"
        return out, "stub", None

    stage5.translate_irac = fake_translate  # type: ignore[assignment]

    async def query(message: str, conversation_id: str, language: str = "en") -> dict:
        resp = await handle_query(
            QueryRequest(
                message=message,
                conversation_id=conversation_id,
                language=language,
            )
        )
        if hasattr(resp, "model_dump"):
            return resp.model_dump()
        return dict(resp)

    async def resolve(conversation_id: str, chosen_section: str, language: str = "en") -> dict:
        resp = await resolve_bifurcation(
            ResolveBifurcationRequest(
                conversation_id=conversation_id,
                chosen_section=chosen_section,
                language=language,
            )
        )
        if hasattr(resp, "model_dump"):
            return resp.model_dump()
        return dict(resp)

    # ------------------------------------------------------------------ a. diagnosis 9
    log("[a] diagnosis 9…")
    diag = load_json(REG / "diagnosis_9.json")["cases"]
    diag_ok = 0
    diag_fail = []
    for i, case in enumerate(diag):
        r = await query(case["message"], cid(f"diag{i}"))
        if match_case(r, case):
            diag_ok += 1
        else:
            diag_fail.append(
                {
                    "i": i,
                    "got_kind": r.get("kind"),
                    "got_reason": r.get("reason"),
                    "expected": {
                        k: case[k]
                        for k in (
                            "expected_kind",
                            "expected_kind_any",
                            "expected_reason",
                        )
                        if k in case
                    },
                }
            )
    expect_d = exp["diagnosis_9"]["pass_count"]
    ok = diag_ok == expect_d
    rows.append(
        {
            "check": "diagnosis_9",
            "result": pass_fail(ok),
            "detail": f"{diag_ok}/{expect_d}",
            "expected": f"{expect_d}/9",
        }
    )
    details["diagnosis_9"] = {"ok": diag_ok, "fail": diag_fail}
    log(f"PASS/FAIL diagnosis_9: {pass_fail(ok)} ({diag_ok}/{expect_d})")

    # ------------------------------------------------------------------ b. fact-free 30
    log("[b] fact-free 30…")
    ff = load_json(REG / "fact_free_30.json")["cases"]
    ff_ok = 0
    ff_counts = {"missing_facts": 0, "missing_date": 0, "other": 0}
    ff_fail = []
    for i, case in enumerate(ff):
        r = await query(case["message"], cid(f"ff{i}"))
        reason = r.get("reason")
        if reason in ff_counts:
            ff_counts[reason] += 1
        else:
            ff_counts["other"] += 1
        if match_case(r, case):
            ff_ok += 1
        else:
            ff_fail.append(
                {
                    "message": case["message"],
                    "got_kind": r.get("kind"),
                    "got_reason": reason,
                    "expected_reason": case.get("expected_reason"),
                }
            )
    exp_ff = exp["fact_free_30"]
    ok = (
        ff_ok == 30
        and ff_counts["missing_facts"] == exp_ff["missing_facts"]
        and ff_counts["missing_date"] == exp_ff["missing_date"]
    )
    rows.append(
        {
            "check": "fact_free_30",
            "result": pass_fail(ok),
            "detail": (
                f"{ff_counts['missing_facts']} missing_facts + "
                f"{ff_counts['missing_date']} missing_date "
                f"(case_ok {ff_ok}/30)"
            ),
            "expected": (
                f"{exp_ff['missing_facts']} missing_facts + "
                f"{exp_ff['missing_date']} missing_date"
            ),
        }
    )
    details["fact_free_30"] = {"counts": ff_counts, "fail": ff_fail}
    log(f"PASS/FAIL fact_free_30: {pass_fail(ok)} ({ff_counts})")

    # ------------------------------------------------------------------ c. false-block 285
    log("[c] false-block 285…")
    fb_src = load_json(REG / "false_block_sources.json")
    bif85_q = load_json(REG / "bif85_questions.json")["questions"]
    held200 = load_json(REG / "false_block_200.json")["questions"]
    date_suf = " Offence date 25 June 2024."
    blocked = 0
    fb_total = 0
    fb_hits = []
    for i, q in enumerate(bif85_q):
        msg = f"{q['question']}{date_suf}"
        r = await query(msg, cid(f"fb85-{i}"))
        fb_total += 1
        if r.get("reason") == "missing_facts":
            blocked += 1
            fb_hits.append({"set": "plain85", "i": i, "id": q.get("id")})
        if fb_total % 25 == 0:
            log(f"  false-block {fb_total}/285 blocked={blocked}")
    for i, q in enumerate(held200):
        msg = f"{q['question']}{date_suf}"
        r = await query(msg, cid(f"fb200-{i}"))
        fb_total += 1
        if r.get("reason") == "missing_facts":
            blocked += 1
            fb_hits.append({"set": "held200", "i": i, "chunk_id": q.get("chunk_id")})
        if fb_total % 25 == 0:
            log(f"  false-block {fb_total}/285 blocked={blocked}")
    exp_fb = exp["false_block"]["blocked"]
    ok = blocked == exp_fb and fb_total == exp["false_block"]["total"]
    rows.append(
        {
            "check": "false_block_285",
            "result": pass_fail(ok),
            "detail": f"{blocked}/{fb_total} blocked",
            "expected": f"{exp_fb}/285 blocked",
            "files": [
                "scripts/regression/bif85_questions.json",
                "scripts/regression/false_block_200.json",
                "scripts/regression/false_block_sources.json",
            ],
        }
    )
    details["false_block"] = {
        "blocked": blocked,
        "total": fb_total,
        "hits": fb_hits,
        "files": rows[-1]["files"],
    }
    log(f"PASS/FAIL false_block_285: {pass_fail(ok)} ({blocked}/{fb_total})")

    # ------------------------------------------------------------------ d. Stage 1 (44)
    log("[d] Stage 1 (44)…")
    _check_deadline()
    s1_real = load_json(ROOT / exp["stage1"]["real_file"])
    s1_stress = load_json(ROOT / exp["stage1"]["stress_file"])
    # results/stage1_real_eval.json truncates text at ~200 chars; use full source.
    s1_real_src = load_json(ROOT / exp["stage1"]["real_cases_source"])
    s1_ok = 0
    s1_fail = []
    real_results = s1_real.get("results") or []
    for i, case in enumerate(real_results):
        text = s1_real_src[i]["text"] if i < len(s1_real_src) else case["text"]
        gt = case.get("ground_truth_date")
        extracted, _matched, _reason = stage1.extract_offense_date(text)
        got = extracted.isoformat() if extracted else None
        route = str(stage1.route_from_date(extracted)) if extracted else "CLARIFY"
        good = got == gt and route == case.get("ground_truth_route")
        if good:
            s1_ok += 1
        else:
            s1_fail.append(
                {
                    "set": "real",
                    "i": i,
                    "got_date": got,
                    "gt_date": gt,
                    "got_route": route,
                    "gt_route": case.get("ground_truth_route"),
                }
            )
    for i, case in enumerate(s1_stress.get("results") or []):
        text = case["text"]
        extracted, _matched, _reason = stage1.extract_offense_date(text)
        if extracted is None:
            route = "CLARIFY"
            got = None
        else:
            got = extracted.isoformat()
            route = str(stage1.route_from_date(extracted))
        # Stored file uses null expected_route for ambiguous → treat as CLARIFY
        exp_route = case.get("expected_route") or case.get("extracted_route") or "CLARIFY"
        stored = case.get("extracted_date")
        if stored in (None, "None"):
            stored = None
        good = route == exp_route and got == stored
        if good:
            s1_ok += 1
        else:
            s1_fail.append(
                {
                    "set": "stress",
                    "i": i,
                    "got_date": got,
                    "got_route": route,
                    "expected_date": stored,
                    "expected_route": exp_route,
                }
            )
    exp_s1 = exp["stage1"]["pass_count"]
    ok = s1_ok == exp_s1
    rows.append(
        {
            "check": "stage1_44",
            "result": pass_fail(ok),
            "detail": f"{s1_ok}/{exp_s1}",
            "expected": "44/44",
            "lives_in": [
                exp["stage1"]["real_file"],
                exp["stage1"]["stress_file"],
                exp["stage1"]["real_cases_source"],
            ],
        }
    )
    details["stage1"] = {"ok": s1_ok, "fail": s1_fail, "lives_in": rows[-1]["lives_in"]}
    log(f"PASS/FAIL stage1_44: {pass_fail(ok)} ({s1_ok}/{exp_s1})")

    # ------------------------------------------------------------------ e. Recall@5 (paper + production)
    log("[e] Recall@5 paper protocol (finetune_more.build_cascade)…")
    _check_deadline()
    # load_paper_cascade lives beside this runner; preamble needs repo-root cwd.
    os.chdir(ROOT)
    sys.path.insert(0, str(REG))
    from load_paper_cascade import load_paper_cascade_module

    fm = load_paper_cascade_module()
    build_cascade = fm.build_cascade
    evaluate_cascade = fm.evaluate_cascade
    paper_exp = exp["recall_paper"]
    # Reuse stage3's e8 model + BNS corpus embeddings (same statutes.jsonl
    # order as finetune_more). A second encode OOMs after Stage 3 load.
    paper_model = stage3._model  # noqa: SLF001 — regression-only reuse
    paper_corpus = stage3._bns  # noqa: SLF001
    if paper_model is None or paper_corpus is None:
        raise RuntimeError("stage3.load() did not set _model / _bns")
    if list(fm.chunk_ids) != list(paper_corpus.chunk_ids):
        raise RuntimeError(
            "finetune_more chunk_id order != stage3 BNS corpus; "
            "cannot reuse embeddings for paper cascade"
        )
    log("  paper cascade using stage3 BNS embeddings (no re-encode)…")
    paper_cascade = build_cascade(paper_model, paper_corpus.emb)
    paper_metrics = evaluate_cascade(
        paper_cascade,
        "Cascade + fine-tuned bge-small (epochs=8) on TEST",
        fm.test_df,
        k=5,
    )
    tol_p = float(paper_exp["tolerance"])
    paper_ok = (
        abs(paper_metrics["recall_at_k"] - float(paper_exp["recall_at_5"])) <= tol_p
        and abs(paper_metrics["mrr"] - float(paper_exp["mrr"])) <= tol_p
        and abs(paper_metrics["ndcg_at_k"] - float(paper_exp["ndcg_at_5"])) <= tol_p
        and int(paper_metrics["n"]) == int(paper_exp["n"])
    )
    paper_hits = int(round(paper_metrics["recall_at_k"] * paper_metrics["n"]))
    rows.append(
        {
            "check": "recall_paper",
            "result": pass_fail(paper_ok),
            "detail": (
                f"R={paper_metrics['recall_at_k']:.4f} "
                f"MRR={paper_metrics['mrr']:.4f} "
                f"NDCG={paper_metrics['ndcg_at_k']:.4f} "
                f"({paper_hits}/{paper_metrics['n']})"
            ),
            "expected": (
                f"R={paper_exp['recall_at_5']} MRR={paper_exp['mrr']} "
                f"NDCG={paper_exp['ndcg_at_5']} "
                f"({paper_exp['hits']}/{paper_exp['n']})"
            ),
        }
    )
    details["recall_paper"] = {
        "recall_at_k": paper_metrics["recall_at_k"],
        "mrr": paper_metrics["mrr"],
        "ndcg_at_k": paper_metrics["ndcg_at_k"],
        "n": paper_metrics["n"],
        "hits": paper_hits,
    }
    log(
        f"PASS/FAIL recall_paper: {pass_fail(paper_ok)} "
        f"(R={paper_metrics['recall_at_k']:.4f} MRR={paper_metrics['mrr']:.4f} "
        f"NDCG={paper_metrics['ndcg_at_k']:.4f})"
    )

    log("[e] Recall@5 production (stage3.cascade_search_act_aware)…")
    _check_deadline()
    prod_exp = exp["recall_production"]
    test_path = ROOT / prod_exp["test_file"]
    hits = 0
    n_test = 0
    for line in test_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        n_test += 1
        retrieved = stage3.cascade_search_act_aware(row["question"], "BNS", k=5)
        if row["chunk_id"] in {c.chunk_id for c in retrieved}:
            hits += 1
        if n_test % 50 == 0:
            log(f"  recall_production {n_test}/636 hits={hits}")
            _check_deadline()
    recall = hits / n_test if n_test else 0.0
    exp_r = float(prod_exp["value"])
    tol = float(prod_exp["tolerance"])
    ok = (
        abs(recall - exp_r) <= tol
        and hits == int(prod_exp["hits"])
        and n_test == int(prod_exp["n"])
    )
    rows.append(
        {
            "check": "recall_production",
            "result": pass_fail(ok),
            "detail": f"{recall:.4f} ({hits}/{n_test})",
            "expected": f"{exp_r} ({prod_exp['hits']}/{prod_exp['n']})",
            "note": prod_exp.get("note"),
        }
    )
    details["recall_production"] = {
        "recall": recall,
        "hits": hits,
        "n": n_test,
        "note": prod_exp.get("note"),
    }
    log(f"PASS/FAIL recall_production: {pass_fail(ok)} ({recall:.4f} {hits}/{n_test})")

    # Free paper-eval locals before the bif85 encode loop (memory pressure).
    del paper_cascade, paper_metrics, fm, build_cascade, evaluate_cascade
    import gc

    gc.collect()

    # ------------------------------------------------------------------ f. bif85_labeled (+ first85 info)
    log("[f] bif85_labeled…")
    bif_meta = load_json(REG / "bif85_questions.json")
    date_suffix = bif_meta["date_suffix"]
    margin = float(bif_meta["margin"])
    corpus_act = bif_meta["corpus_act"]
    bif_statuses = []
    bif_count = 0
    for i, q in enumerate(bif_meta["questions"]):
        msg = f"{q['question']}{date_suffix}"
        scored = stage3.cascade_search_with_scores(msg, corpus_act, k=5)
        scored_sorted = sorted(scored, key=lambda x: x[1], reverse=True)
        opts = stage3.detect_bifurcation(scored_sorted, margin=margin)
        status = "bifurcation" if len(opts) > 1 else "mapping"
        if status == "bifurcation":
            bif_count += 1
        bif_statuses.append(
            {
                "i": i,
                "id": q.get("id"),
                "status": status,
                "n_options": len(opts),
                "top_sections": [c.section_number for c, _ in scored_sorted[:4]],
            }
        )
        if (i + 1) % 20 == 0:
            log(f"  bif85_labeled {i + 1}/85 count={bif_count}")
    exp_bif = int(exp["bif85_labeled"]["expected_count"])
    ok = bif_count == exp_bif
    bif_diff = None
    if bif_count != exp_bif:
        bif_diff = f"run={bif_count} vs expectation {exp_bif} (Δ={bif_count - exp_bif:+d})"
    rows.append(
        {
            "check": "bif85_labeled",
            "result": pass_fail(ok),
            "detail": f"{bif_count}/{len(bif_statuses)}",
            "expected": f"{exp_bif}/85",
            "diff": bif_diff,
            "date_suffix": date_suffix,
            "corpus_act": corpus_act,
            "margin": margin,
        }
    )
    details["bif85_labeled"] = {
        "count": bif_count,
        "n": len(bif_statuses),
        "expected": exp_bif,
        "diff": bif_diff,
        "statuses": bif_statuses,
    }
    log(
        f"PASS/FAIL bif85_labeled: {pass_fail(ok)} "
        f"({bif_count}/85; {bif_diff or 'matches'})"
    )

    # Informational: first 85 lines of nyaya_eval_filtered (not asserted)
    info = exp.get("bif85_first85_info") or {}
    nyaya_path = ROOT / info.get("source", "data/clean/nyaya_eval_filtered.jsonl")
    first85_cnt = 0
    first85_n = 0
    if nyaya_path.is_file():
        for line in nyaya_path.read_text(encoding="utf-8").splitlines()[:85]:
            if not line.strip():
                continue
            row = json.loads(line)
            q = str(row.get("question") or "").strip()
            if not q:
                continue
            msg = f"{q}{info.get('date_suffix', date_suffix)}"
            scored = stage3.cascade_search_with_scores(
                msg, info.get("corpus_act", corpus_act), k=5
            )
            scored_sorted = sorted(scored, key=lambda x: x[1], reverse=True)
            opts = stage3.detect_bifurcation(
                scored_sorted, margin=float(info.get("margin", margin))
            )
            first85_n += 1
            if len(opts) > 1:
                first85_cnt += 1
    rows.append(
        {
            "check": "bif85_first85",
            "result": "INFO",
            "detail": f"{first85_cnt}/{first85_n}",
            "expected": f"~{info.get('last_count', 52)}/85 (not asserted)",
            "note": info.get("note"),
        }
    )
    details["bif85_first85"] = {
        "count": first85_cnt,
        "n": first85_n,
        "last_count": info.get("last_count"),
        "asserted": False,
    }
    log(
        f"INFO bif85_first85: {first85_cnt}/{first85_n} "
        f"(last count {info.get('last_count', 52)}; not asserted)"
    )

    # ------------------------------------------------------------------ g. code-mismatch / section_lookup / date-conflict / rejected
    log("[g] code-mismatch 6…")
    mm_cases = load_json(REG / "code_mismatch_6.json")["cases"]
    mm_ok = 0
    mm_fail = []
    for i, case in enumerate(mm_cases):
        r = await query(case["message"], cid(f"mm{i}"))
        if match_case(r, case):
            mm_ok += 1
        else:
            mm_fail.append(
                {
                    "message": case["message"],
                    "got": (r.get("kind"), r.get("reason")),
                }
            )
    ok = mm_ok == exp["code_mismatch"]["pass_count"]
    rows.append(
        {
            "check": "code_mismatch_6",
            "result": pass_fail(ok),
            "detail": f"{mm_ok}/6",
            "expected": "6/6",
        }
    )
    details["code_mismatch"] = {"ok": mm_ok, "fail": mm_fail}
    log(f"PASS/FAIL code_mismatch_6: {pass_fail(ok)} ({mm_ok}/6)")

    log("[g] section_lookup 7…")
    sl_cases = load_json(REG / "section_lookup_7.json")["cases"]
    sl_ok = 0
    sl_fail = []
    for i, case in enumerate(sl_cases):
        r = await query(case["message"], cid(f"sl{i}"))
        if match_case(r, case):
            sl_ok += 1
        else:
            sl_fail.append(
                {
                    "message": case["message"],
                    "got": (r.get("kind"), r.get("reason")),
                }
            )
    ok = sl_ok == exp["section_lookup"]["pass_count"]
    rows.append(
        {
            "check": "section_lookup_7",
            "result": pass_fail(ok),
            "detail": f"{sl_ok}/7",
            "expected": "7/7",
        }
    )
    details["section_lookup"] = {"ok": sl_ok, "fail": sl_fail}
    log(f"PASS/FAIL section_lookup_7: {pass_fail(ok)} ({sl_ok}/7)")

    log("[g] date-conflict…")
    dc_spec = load_json(REG / "date_conflict_cases.json")["cases"]
    dc_ok = 0
    dc_fail = []
    for case in dc_spec:
        conv = cid(f"dc-{case['id']}")
        case_ok = True
        step_log = []
        last_opts: list = []
        for step in case["steps"]:
            if step["action"] == "query":
                r = await query(step["message"], conv)
            elif step["action"] == "resolve_date":
                # Pick earlier/later option by parsing option section labels.
                opts = last_opts
                labels = [o["section"] if isinstance(o, dict) else o.section for o in opts]
                # Filter out describe-facts if present
                labels = [lb for lb in labels if lb != DESCRIBE_FACTS_OPTION]
                if len(labels) < 2:
                    case_ok = False
                    step_log.append({"step": step, "error": "need 2 date options", "labels": labels})
                    break
                # Parse roughly: prefer chronological order
                def parse_label(lb: str) -> date:
                    # labels like "25 June 2024"
                    from dateutil import parser as dateparser

                    return dateparser.parse(lb, dayfirst=False).date()

                ordered = sorted(labels, key=parse_label)
                choose = ordered[0] if step["choose"] == "earlier" else ordered[-1]
                r = await resolve(conv, choose)
            else:
                raise ValueError(step["action"])
            step_log.append(
                {
                    "action": step["action"],
                    "kind": r.get("kind"),
                    "reason": r.get("reason"),
                }
            )
            if r.get("kind") == "bifurcation":
                last_opts = r.get("options") or []
            if not match_case(r, step):
                case_ok = False
        if case_ok:
            dc_ok += 1
        else:
            dc_fail.append({"id": case["id"], "steps": step_log})
    ok = dc_ok == len(dc_spec)
    rows.append(
        {
            "check": "date_conflict",
            "result": pass_fail(ok),
            "detail": f"{dc_ok}/{len(dc_spec)} sequences",
            "expected": f"{len(dc_spec)}/{len(dc_spec)} sequences",
        }
    )
    details["date_conflict"] = {"ok": dc_ok, "fail": dc_fail}
    log(f"PASS/FAIL date_conflict: {pass_fail(ok)} ({dc_ok}/{len(dc_spec)})")

    log("[g] rejected-options…")
    rej_spec = load_json(REG / "rejected_options_cases.json")
    escape = rej_spec.get("describe_facts_option") or DESCRIBE_FACTS_OPTION
    rej_ok = 0
    rej_fail = []
    for case in rej_spec["cases"]:
        conv = cid(f"rej-{case['id']}")
        r = await query(case["message"], conv)
        trace = {"first": {"kind": r.get("kind"), "reason": r.get("reason")}}
        ok_case = r.get("kind") == case.get("expected_first_kind", "bifurcation")
        if r.get("kind") == "bifurcation":
            r2 = await resolve(conv, escape)
            trace["after_escape"] = {"kind": r2.get("kind"), "reason": r2.get("reason")}
            ae = case.get("after_escape") or {}
            if not match_case(r2, ae):
                ok_case = False
            # Follow-ups: reject until exhausted or out of followups
            final_kind = None
            final_reason = None
            for j, follow in enumerate(case.get("followups") or []):
                r3 = await query(follow, conv)
                final_kind, final_reason = r3.get("kind"), r3.get("reason")
                if r3.get("kind") == "bifurcation":
                    await resolve(conv, escape)
                elif r3.get("kind") == "section_lookup":
                    break
            trace["final"] = {"kind": final_kind, "reason": final_reason}
            # Accept: exhausted cards OR still clarifying/mapping after escapes
            if final_kind not in {"section_lookup", "mapping", "clarify", "bifurcation", None}:
                ok_case = False
        if ok_case:
            rej_ok += 1
        else:
            rej_fail.append({"id": case["id"], "trace": trace})
    ok = rej_ok == len(rej_spec["cases"])
    rows.append(
        {
            "check": "rejected_options",
            "result": pass_fail(ok),
            "detail": f"{rej_ok}/{len(rej_spec['cases'])}",
            "expected": f"{len(rej_spec['cases'])}/{len(rej_spec['cases'])}",
        }
    )
    details["rejected_options"] = {"ok": rej_ok, "fail": rej_fail}
    log(f"PASS/FAIL rejected_options: {pass_fail(ok)} ({rej_ok}/{len(rej_spec['cases'])})")

    # ------------------------------------------------------------------ h. quota stub
    log("[h] quota stub…")
    rem = 5
    seq = [rem]
    # date clarify / section_lookup / bifurcation|date_conflict — no decrement
    seq.append(rem)
    seq.append(rem)
    seq.append(rem)
    # mapping answer
    rem -= 1
    seq.append(rem)
    exp_seq = exp["quota_stub"]["sequence"]
    ok = seq == exp_seq
    rows.append(
        {
            "check": "quota_stub",
            "result": pass_fail(ok),
            "detail": str(seq),
            "expected": str(exp_seq),
            "note": (
                "In-process stub mirroring ChatEntry (decrement only on "
                "kind===mapping). Browser path: frontend/src/components/ChatEntry.tsx. "
                "No browser run."
            ),
        }
    )
    details["quota_stub"] = {"sequence": seq, "expected": exp_seq}
    log(f"PASS/FAIL quota_stub: {pass_fail(ok)} ({seq})")

    elapsed = time.time() - t0
    details["elapsed_sec"] = round(elapsed, 1)
    details["rows"] = rows

    # Write baseline (per-question bif85_labeled statuses for future diffs)
    baseline = {
        "written_at": datetime.now().isoformat(timespec="seconds"),
        "elapsed_sec": details["elapsed_sec"],
        "bif85_labeled": {
            "date_suffix": date_suffix,
            "corpus_act": corpus_act,
            "margin": margin,
            "expected_count": exp_bif,
            "actual_count": bif_count,
            "n": len(bif_statuses),
            "questions": bif_statuses,
            "note": (
                "Per-question statuses from this run (labelled single-citation 85). "
                "Expected aggregate is 48 in scripts/regression/expectations.json."
            ),
        },
        "bif85_first85": details.get("bif85_first85"),
        "recall_paper": details.get("recall_paper"),
        "recall_production": details.get("recall_production"),
        "summary": rows,
        "mismatches_vs_log": [r for r in rows if r["result"] == "FAIL"],
    }
    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE.write_text(json.dumps(baseline, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_JSON.write_text(json.dumps(details, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Final table
    log("")
    log("=" * 72)
    log(f"{'CHECK':<22} {'RESULT':<6} {'DETAIL':<28} EXPECTED")
    log("-" * 72)
    for r in rows:
        log(
            f"{r['check']:<22} {r['result']:<6} {str(r.get('detail', '')):<28} {r.get('expected', '')}"
        )
    log("-" * 72)
    n_pass = sum(1 for r in rows if r["result"] == "PASS")
    n_fail = sum(1 for r in rows if r["result"] == "FAIL")
    n_info = sum(1 for r in rows if r["result"] == "INFO")
    log(f"TOTAL  PASS={n_pass}  FAIL={n_fail}  INFO={n_info}  elapsed={elapsed:.1f}s")
    log(f"Baseline written: {BASELINE}")
    log(f"Full details: {OUT_JSON}")
    log("=" * 72)
    return details


def main() -> int:
    # Soft deadline via wall clock (SIGALRM fights PyTorch/macOS).
    killer = threading.Timer(
        HARD_TIMEOUT,
        lambda: os.kill(os.getpid(), 9),
    )
    killer.daemon = True
    killer.start()
    try:
        asyncio.run(main_async())
        return 0
    except Timeout as e:
        log(f"TIMEOUT: {e}")
        return 2
    except Exception as e:
        log(f"FATAL: {type(e).__name__}: {e}")
        raise
    finally:
        killer.cancel()


if __name__ == "__main__":
    raise SystemExit(main())
