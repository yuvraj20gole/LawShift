#!/usr/bin/env python3
"""Live writer + verifier: LAWSHIFT_VERIFY_WITH_APPLICATION on vs off (20 Qs).

Uses real Ollama generate + verify. No `ollama` CLI. Hard timeout via env.

Usage:
  REGRESSION_TIMEOUT_SEC=2400 \\
    ../NLP-Project/.venv/bin/python -u scripts/regression/measure_verify_application_live20.py

Writes results/verify_with_application_live20.json
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

PROG = Path("/tmp/lawshift_verify_live20_prog.txt")
OUT = ROOT / "results" / "verify_with_application_live20.json"
HARD_TIMEOUT = int(os.environ.get("REGRESSION_TIMEOUT_SEC", "2400"))

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
os.environ.setdefault("LAWSHIFT_FIXED_CONCLUSION", "1")
os.environ["LAWSHIFT_VERIFY_WITH_APPLICATION"] = "0"

# 20 fact-bearing questions; first is the IPC 292 bookstore case.
QUESTIONS = [
    "On 25 June 2024, a bookstore owner sold obscene magazines for the first time.",
    "On 5 September 2024, a person was found in possession of counterfeit currency notes.",
    "On 10 August 2024, a riot occurred for a landowner's benefit and the agent failed to prevent it.",
    "On 25 June 2024, a person dishonestly took a mobile phone from a shop counter without paying.",
    "On 10 August 2024, a driver hit a pedestrian and fled without stopping.",
    "On 5 September 2024, a cashier accepted a bribe to clear a file.",
    "On 12 March 2024, a landlord locked a tenant out of the flat and kept the belongings.",
    "On 1 July 2024, a person forged a signature on a property sale deed.",
    "On 20 June 2024, two people fought in a market and one caused a simple hurt injury.",
    "On 15 August 2024, a person threatened another with a knife to take their wallet.",
    "On 3 May 2024, a shopkeeper sold food knowing it was unfit for human consumption.",
    "On 22 September 2024, a person broke into a house at night to commit theft.",
    "On 8 June 2024, a public servant used a forged certificate to obtain a job.",
    "On 25 June 2024, a person made a false statement under oath in a judicial proceeding.",
    "On 2 August 2024, a doctor operated without consent and caused grievous hurt.",
    "On 18 June 2024, a person kidnapped a child from a school gate.",
    "On 11 September 2024, a company director cheated investors with a false prospectus.",
    "On 30 June 2024, a person defamed another in a newspaper article.",
    "On 7 July 2024, a person caused death by rash driving on a highway.",
    "On 14 March 2024, a person voluntarily caused hurt with a dangerous weapon.",
]


def log(msg: str) -> None:
    line = msg if msg.endswith("\n") else msg + "\n"
    with PROG.open("a", encoding="utf-8") as f:
        f.write(line)
    print(msg, flush=True)


def cid(prefix: str) -> str:
    return f"live20-{prefix}-{uuid.uuid4().hex[:10]}"


async def main_async() -> dict:
    PROG.write_text("", encoding="utf-8")
    t0 = time.time()
    os.chdir(ROOT)

    from app import stage3, stage4
    from app.main import DESCRIBE_FACTS_OPTION, handle_query, resolve_bifurcation
    from app.schemas import QueryRequest, ResolveBifurcationRequest

    log("[live20] loading Stage 3…")
    stage3.load()
    log(f"[live20] Stage 3 loaded in {time.time() - t0:.1f}s")

    real_verify = stage4.verify_rule_only_14b_v2
    verify_timings: list[dict] = []

    def timed_verify(rule_text, conclusion_text, application_text=None):
        mode = "with_application" if application_text is not None else "rule_conclusion"
        start = time.time()
        try:
            verdict, explanation = real_verify(
                rule_text, conclusion_text, application_text=application_text
            )
            err = None
        except Exception as exc:  # noqa: BLE001
            verdict, explanation = "SUPPORTED", f"error: {exc}"
            err = str(exc)
        elapsed_ms = round((time.time() - start) * 1000, 1)
        verify_timings.append(
            {
                "mode": mode,
                "elapsed_ms": elapsed_ms,
                "verdict": verdict,
                "flagged": verdict == "NOT_SUPPORTED",
                "error": err,
            }
        )
        return verdict, explanation

    stage4.verify_rule_only_14b_v2 = timed_verify  # type: ignore[assignment]

    async def query(message: str, conversation_id: str) -> dict:
        resp = await handle_query(
            QueryRequest(
                message=message,
                conversation_id=conversation_id,
                language="en",
            )
        )
        return resp.model_dump() if hasattr(resp, "model_dump") else dict(resp)

    async def resolve(conversation_id: str, chosen: str) -> dict:
        resp = await resolve_bifurcation(
            ResolveBifurcationRequest(
                conversation_id=conversation_id,
                chosen_section=chosen,
            )
        )
        return resp.model_dump() if hasattr(resp, "model_dump") else dict(resp)

    async def to_mapping(message: str, tag: str) -> dict:
        conv = cid(tag)
        r = await query(message, conv)
        if r.get("kind") == "bifurcation":
            opts = r.get("options") or []
            choice = None
            for o in opts:
                sec = o.get("section") if isinstance(o, dict) else str(o)
                if sec and sec != DESCRIBE_FACTS_OPTION:
                    choice = sec
                    break
            if choice is None and opts:
                choice = (
                    opts[0].get("section") if isinstance(opts[0], dict) else str(opts[0])
                )
            if choice:
                r = await resolve(conv, choice)
        return r

    rows: list[dict] = []
    for i, message in enumerate(QUESTIONS):
        tag = f"q{i:02d}"
        row: dict = {"id": tag, "message": message}

        os.environ["LAWSHIFT_VERIFY_WITH_APPLICATION"] = "0"
        verify_timings.clear()
        t_ans = time.time()
        r_off = await to_mapping(message, f"{tag}-off")
        ans_off_ms = round((time.time() - t_ans) * 1000, 1)
        app = (r_off.get("application_text") or r_off.get("irac", {}).get("application") or "")
        row["off"] = {
            "kind": r_off.get("kind"),
            "answer_ms": ans_off_ms,
            "section": (r_off.get("badge") or {}).get("section"),
            "code": (r_off.get("badge") or {}).get("code"),
            "rule_truncated": r_off.get("rule_truncated"),
            "flagged": bool(r_off.get("verification", {}).get("flagged"))
            if r_off.get("kind") == "mapping"
            else None,
            "verify_calls": list(verify_timings),
            "application_mentions_exception": (
                "exception" in app.lower() if r_off.get("kind") == "mapping" else None
            ),
            "application_preview": app[:240] if r_off.get("kind") == "mapping" else None,
        }

        os.environ["LAWSHIFT_VERIFY_WITH_APPLICATION"] = "1"
        verify_timings.clear()
        t_ans = time.time()
        r_on = await to_mapping(message, f"{tag}-on")
        ans_on_ms = round((time.time() - t_ans) * 1000, 1)
        app_on = (
            r_on.get("application_text") or r_on.get("irac", {}).get("application") or ""
        )
        row["on"] = {
            "kind": r_on.get("kind"),
            "answer_ms": ans_on_ms,
            "section": (r_on.get("badge") or {}).get("section"),
            "code": (r_on.get("badge") or {}).get("code"),
            "rule_truncated": r_on.get("rule_truncated"),
            "flagged": bool(r_on.get("verification", {}).get("flagged"))
            if r_on.get("kind") == "mapping"
            else None,
            "verify_calls": list(verify_timings),
            "application_mentions_exception": (
                "exception" in app_on.lower() if r_on.get("kind") == "mapping" else None
            ),
            "application_preview": app_on[:240] if r_on.get("kind") == "mapping" else None,
        }
        rows.append(row)
        log(
            f"[{tag}] off={row['off']['kind']}/{row['off'].get('code')} "
            f"{row['off'].get('section')} {row['off']['answer_ms']}ms "
            f"flagged={row['off']['flagged']} | "
            f"on={row['on']['kind']} {row['on']['answer_ms']}ms "
            f"flagged={row['on']['flagged']} "
            f"app_exc={row['on']['application_mentions_exception']}"
        )

    def collect(mode_key: str, call_mode: str) -> list[float]:
        out: list[float] = []
        for r in rows:
            for c in r[mode_key]["verify_calls"]:
                if c["mode"] == call_mode:
                    out.append(c["elapsed_ms"])
        return out

    ans_off = [r["off"]["answer_ms"] for r in rows if r["off"]["kind"] == "mapping"]
    ans_on = [r["on"]["answer_ms"] for r in rows if r["on"]["kind"] == "mapping"]
    v_off = collect("off", "rule_conclusion")
    v_on = collect("on", "with_application")

    def stats(xs: list[float]) -> dict:
        if not xs:
            return {"n": 0, "mean": None, "max": None, "min": None, "per_call": []}
        return {
            "n": len(xs),
            "mean": round(sum(xs) / len(xs), 1),
            "max": max(xs),
            "min": min(xs),
            "per_call": xs,
        }

    summary = {
        "env": "LAWSHIFT_VERIFY_WITH_APPLICATION",
        "default": "0 (OFF)",
        "n_questions": len(rows),
        "n_mapping_off": sum(1 for r in rows if r["off"]["kind"] == "mapping"),
        "n_mapping_on": sum(1 for r in rows if r["on"]["kind"] == "mapping"),
        "applications_flagged_off": sum(1 for r in rows if r["off"].get("flagged") is True),
        "applications_flagged_on": sum(1 for r in rows if r["on"].get("flagged") is True),
        "answer_latency_ms_off": stats(ans_off),
        "answer_latency_ms_on": stats(ans_on),
        "verify_latency_ms_off": stats(v_off),
        "verify_latency_ms_on": stats(v_on),
        "ipc292_row": rows[0] if rows else None,
        "note": "Real writer (3B) + real verifier (14B). Generate not stubbed.",
    }
    out = {
        "written_at": datetime.now().isoformat(timespec="seconds"),
        "elapsed_sec": round(time.time() - t0, 1),
        "summary": summary,
        "rows": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(json.dumps({k: v for k, v in summary.items() if k != "ipc292_row"}, indent=2))
    log(f"IPC292 detail: {json.dumps(summary.get('ipc292_row'), indent=2)}")
    log(f"Wrote {OUT}")
    return out


def main() -> int:
    killer = threading.Timer(HARD_TIMEOUT, lambda: os.kill(os.getpid(), 9))
    killer.daemon = True
    killer.start()
    try:
        asyncio.run(main_async())
        return 0
    finally:
        killer.cancel()


if __name__ == "__main__":
    raise SystemExit(main())
