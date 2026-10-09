#!/usr/bin/env python3
"""Measure LAWSHIFT_VERIFY_WITH_APPLICATION on/off (default remains OFF).

Runs the 9 diagnosis cases plus 10 fact-bearing questions. Stage 4 generate is
stubbed; the 14B verifier is called for real so Application-flag latency is
isolated. No `ollama` CLI commands.

Usage (repo root, hard timeout):
  /usr/bin/time -p env REGRESSION_TIMEOUT_SEC=900 \\
    ../NLP-Project/.venv/bin/python -u scripts/regression/measure_verify_application.py

Writes results/verify_with_application_measure.json
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
REG = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

PROG = Path("/tmp/lawshift_verify_app_measure_prog.txt")
OUT = ROOT / "results" / "verify_with_application_measure.json"
HARD_TIMEOUT = int(os.environ.get("REGRESSION_TIMEOUT_SEC", "900"))

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
os.environ.setdefault("LAWSHIFT_FIXED_CONCLUSION", "1")
# Measurement toggles the flag explicitly; keep default path off in process until then.
os.environ["LAWSHIFT_VERIFY_WITH_APPLICATION"] = "0"

EXTRA_10 = [
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
]


def log(msg: str) -> None:
    line = msg if msg.endswith("\n") else msg + "\n"
    with PROG.open("a", encoding="utf-8") as f:
        f.write(line)
    print(msg, flush=True)


def cid(prefix: str) -> str:
    return f"meas-app-{prefix}-{uuid.uuid4().hex[:10]}"


async def main_async() -> dict:
    PROG.write_text("", encoding="utf-8")
    t0 = time.time()
    os.chdir(ROOT)

    from app import stage3, stage4
    from app.main import DESCRIBE_FACTS_OPTION, handle_query, resolve_bifurcation
    from app.schemas import QueryRequest, ResolveBifurcationRequest

    log("[measure] loading Stage 3…")
    stage3.load()
    log(f"[measure] Stage 3 loaded in {time.time() - t0:.1f}s")

    def fake_generate(question, retrieved_text, source_citation):
        return (
            "Issue: Whether the facts engage the cited section.\n"
            "Application: The facts as described are compared with the elements "
            "in the statutory text; unstated elements are not established.\n"
        )

    stage4.generate_irac = fake_generate  # type: ignore[assignment]

    # Keep real verify; wrap to time each call.
    real_verify = stage4.verify_rule_only_14b_v2
    timings: list[dict] = []

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
        timings.append(
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
        if hasattr(resp, "model_dump"):
            return resp.model_dump()
        return dict(resp)

    async def resolve(conversation_id: str, chosen: str) -> dict:
        resp = await resolve_bifurcation(
            ResolveBifurcationRequest(
                conversation_id=conversation_id,
                chosen_section=chosen,
            )
        )
        if hasattr(resp, "model_dump"):
            return resp.model_dump()
        return dict(resp)

    async def to_mapping(message: str, tag: str) -> dict:
        """Query; if bifurcation, pick first option (not describe-facts)."""
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

    diag = json.loads((REG / "diagnosis_9.json").read_text(encoding="utf-8"))
    messages: list[tuple[str, str]] = [
        (f"diag_{i}", c["message"]) for i, c in enumerate(diag["cases"])
    ]
    for i, m in enumerate(EXTRA_10):
        messages.append((f"extra_{i}", m))

    rows: list[dict] = []
    for tag, message in messages:
        row: dict = {"id": tag, "message": message}
        # Flag OFF
        os.environ["LAWSHIFT_VERIFY_WITH_APPLICATION"] = "0"
        timings.clear()
        t_ans = time.time()
        r_off = await to_mapping(message, f"{tag}-off")
        ans_off_ms = round((time.time() - t_ans) * 1000, 1)
        v_off = [t for t in timings if t["mode"] == "rule_conclusion"]
        row["off"] = {
            "kind": r_off.get("kind"),
            "answer_ms": ans_off_ms,
            "has_application": bool((r_off.get("application_text") or "").strip())
            if r_off.get("kind") == "mapping"
            else False,
            "verify_calls": list(v_off),
            "flagged": bool(r_off.get("verification", {}).get("flagged"))
            if r_off.get("kind") == "mapping"
            else None,
        }

        # Flag ON
        os.environ["LAWSHIFT_VERIFY_WITH_APPLICATION"] = "1"
        timings.clear()
        t_ans = time.time()
        r_on = await to_mapping(message, f"{tag}-on")
        ans_on_ms = round((time.time() - t_ans) * 1000, 1)
        v_on = [t for t in timings if t["mode"] == "with_application"]
        row["on"] = {
            "kind": r_on.get("kind"),
            "answer_ms": ans_on_ms,
            "has_application": bool((r_on.get("application_text") or "").strip())
            if r_on.get("kind") == "mapping"
            else False,
            "verify_calls": list(v_on),
            "flagged": bool(r_on.get("verification", {}).get("flagged"))
            if r_on.get("kind") == "mapping"
            else None,
        }
        rows.append(row)
        log(
            f"[{tag}] off={row['off']['kind']}/{row['off']['answer_ms']}ms "
            f"flagged={row['off']['flagged']} | "
            f"on={row['on']['kind']}/{row['on']['answer_ms']}ms "
            f"flagged={row['on']['flagged']}"
        )

    mapping_rows = [r for r in rows if r["off"]["kind"] == "mapping" or r["on"]["kind"] == "mapping"]
    apps_flagged_on = sum(1 for r in rows if r["on"].get("flagged") is True)
    apps_flagged_off = sum(1 for r in rows if r["off"].get("flagged") is True)
    verify_off_ms = [
        c["elapsed_ms"]
        for r in rows
        for c in r["off"]["verify_calls"]
    ]
    verify_on_ms = [
        c["elapsed_ms"]
        for r in rows
        for c in r["on"]["verify_calls"]
    ]

    summary = {
        "env": "LAWSHIFT_VERIFY_WITH_APPLICATION",
        "default": "0 (OFF)",
        "n_messages": len(rows),
        "n_mapping_off": sum(1 for r in rows if r["off"]["kind"] == "mapping"),
        "n_mapping_on": sum(1 for r in rows if r["on"]["kind"] == "mapping"),
        "applications_flagged_off": apps_flagged_off,
        "applications_flagged_on": apps_flagged_on,
        "verify_latency_ms_off": {
            "n": len(verify_off_ms),
            "mean": round(sum(verify_off_ms) / len(verify_off_ms), 1) if verify_off_ms else None,
            "max": max(verify_off_ms) if verify_off_ms else None,
            "min": min(verify_off_ms) if verify_off_ms else None,
            "per_call": verify_off_ms,
        },
        "verify_latency_ms_on": {
            "n": len(verify_on_ms),
            "mean": round(sum(verify_on_ms) / len(verify_on_ms), 1) if verify_on_ms else None,
            "max": max(verify_on_ms) if verify_on_ms else None,
            "min": min(verify_on_ms) if verify_on_ms else None,
            "per_call": verify_on_ms,
        },
        "note": (
            "Generate stubbed; verifier is live 14B. Latency is per answer "
            "(answer_ms) and per verify call. Flag default remains OFF."
        ),
    }
    out = {
        "written_at": datetime.now().isoformat(timespec="seconds"),
        "elapsed_sec": round(time.time() - t0, 1),
        "summary": summary,
        "rows": rows,
        "mapping_ids": [r["id"] for r in mapping_rows],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(json.dumps(summary, indent=2))
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
