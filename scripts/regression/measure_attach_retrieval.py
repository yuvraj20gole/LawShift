#!/usr/bin/env python3
"""Measure attached-facts retrieval vs typed questions (M3).

Writes progress to /tmp/lawshift_m3_measure_prog.txt and results JSON to
/tmp/lawshift_m3_measure_out.json. Hard timeout via REGRESSION_TIMEOUT_SEC.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
import uuid
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REG = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

PROG = Path("/tmp/lawshift_m3_measure_prog.txt")
OUT = Path("/tmp/lawshift_m3_measure_out.json")
HARD = int(os.environ.get("REGRESSION_TIMEOUT_SEC", "1800"))
DEADLINE = time.time() + HARD

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


def check() -> None:
    if time.time() > DEADLINE:
        raise TimeoutError("hard timeout")


def top5_ids(message: str, route: str = "IPC") -> list[str]:
    from app import stage3

    hits = stage3.cascade_search_act_aware(message, route, k=5)
    return [h.chunk_id for h in hits]


def status_kind(resp) -> str:
    kind = getattr(resp, "kind", None) or (resp.get("kind") if isinstance(resp, dict) else None)
    reason = getattr(resp, "reason", None)
    if isinstance(resp, dict):
        reason = resp.get("reason")
    if kind == "bifurcation":
        return f"bifurcation:{reason or 'score_gap'}"
    if kind == "clarify":
        return f"clarify:{reason}"
    if kind == "section_lookup":
        return f"section_lookup:{reason}"
    if kind == "mapping":
        badge = getattr(resp, "badge", None)
        if badge is None and isinstance(resp, dict):
            badge = resp.get("badge") or {}
            return f"mapping:{badge.get('code')} {badge.get('section')}"
        return f"mapping:{badge.code} {badge.section}"
    if kind == "failure":
        return f"failure:{reason}"
    return str(kind)


async def main() -> None:
    PROG.write_text("", encoding="utf-8")
    log("[m3-measure] start")

    from app import stage3, stage4
    from app.case_attach import attach_case, reset_attached_cases
    from app.main import _LOCKED_DATES, handle_query
    from app.schemas import QueryRequest

    def fake_generate(*_a, **_k):
        return (
            "Issue: stub\n\nRule: stub\n\nApplication: stub\n\n"
            "Conclusion: stub"
        )

    def fake_verify(*_a, **_k):
        return "SUPPORTED", "stub"

    stage4.generate_irac = fake_generate  # type: ignore[assignment]
    stage4.verify_rule_only_14b_v2 = fake_verify  # type: ignore[assignment]

    log("[m3-measure] loading Stage 3…")
    stage3.load()
    log("[m3-measure] Stage 3 ready")

    bif = json.loads((REG / "bif85_questions.json").read_text(encoding="utf-8"))
    date_suffix = bif["date_suffix"]
    questions = bif["questions"]
    locked = date(2024, 6, 25)

    part_a = []
    match = 0
    for i, q in enumerate(questions, 1):
        check()
        qtext = (q.get("question") or "").strip()
        typed = f"{qtext}{date_suffix}".strip()
        typed_top = top5_ids(typed, "IPC")

        # Typed path status via handle_query
        reset_attached_cases()
        _LOCKED_DATES.clear()
        cid_t = f"meas-t-{uuid.uuid4().hex[:8]}"
        resp_t = await handle_query(
            QueryRequest(message=typed, conversation_id=cid_t, language="en")
        )
        st_t = status_kind(resp_t)

        # Attach facts = question only; follow-up
        reset_attached_cases()
        _LOCKED_DATES.clear()
        cid_a = f"meas-a-{uuid.uuid4().hex[:8]}"
        attach_case(
            conversation_id=cid_a,
            user_id="measure",
            facts_text=qtext,
            offence_date=locked,
            date_source="document",
            filename=None,
        )
        _LOCKED_DATES[cid_a] = locked
        composed = f"Which section applies?\n\n{qtext}"
        attach_top = top5_ids(composed, "IPC")
        resp_a = await handle_query(
            QueryRequest(
                message="Which section applies?",
                conversation_id=cid_a,
                language="en",
            )
        )
        st_a = status_kind(resp_a)

        same_status = st_t == st_a
        same_top5 = typed_top == attach_top
        ok = same_status and same_top5
        if ok:
            match += 1
        else:
            why = []
            if not same_status:
                why.append(f"status {st_t} vs {st_a}")
            if not same_top5:
                why.append(f"top5 {typed_top} vs {attach_top}")
            part_a.append(
                {
                    "n": i,
                    "id": q.get("id"),
                    "ok": False,
                    "why": "; ".join(why),
                    "typed_status": st_t,
                    "attach_status": st_a,
                    "typed_top5": typed_top,
                    "attach_top5": attach_top,
                }
            )
        if i % 10 == 0:
            log(f"[a] {i}/85 match={match}")

    log(f"[a] done match={match}/85 differ={len(part_a)}")

    # (b) synthetic FIR-like docs
    templates = [
        (
            "IPC_292",
            "The accused bookstore owner sold obscene magazines to customers "
            "for the first time without licence.",
        ),
        (
            "IPC_379",
            "The accused stole a bicycle parked outside the complainant house "
            "and fled on foot.",
        ),
        (
            "IPC_323",
            "The accused voluntarily caused hurt by beating the complainant "
            "with a stick during a quarrel.",
        ),
        (
            "IPC_420",
            "The accused cheated the complainant by dishonestly inducing "
            "delivery of money through a fake investment scheme.",
        ),
        (
            "IPC_506",
            "The accused criminally intimidated the complainant by threatening "
            "to cause death if a complaint was filed.",
        ),
    ]
    lengths = [500, 1500, 3000, 6000]
    part_b = []
    for length in lengths:
        for pos in ("start", "end"):
            for gold, core in templates[:2]:  # 2 templates × 2 pos × 4 lengths = 16; need 10
                pass
    # Build exactly 10: 4 lengths × start/end for first template + 2 more
    built = 0
    for length in lengths:
        for pos in ("start", "end"):
            if built >= 10:
                break
            gold, core = templates[built % len(templates)]
            pad = (" filler clause about residence and witnesses. " * 400)
            if pos == "start":
                body = (core + " " + pad)[:length]
            else:
                body = (pad + " " + core)
                body = body[-length:] if len(body) > length else body
            # Ensure core present
            if core.split()[2] not in body:
                if pos == "start":
                    body = (core + " " + body)[:length]
                else:
                    body = (body + " " + core)[-length:]
            msg = f"Which section applies?\n\n{body}"
            top = top5_ids(msg, "IPC")
            in5 = gold in top or gold.replace("IPC_", "IPC_") in top
            # Also accept bare section match
            sec = gold.split("_", 1)[1]
            in5 = any(sec in (t or "") for t in top)
            in1 = bool(top) and sec in (top[0] or "")
            part_b.append(
                {
                    "n": built + 1,
                    "length": length,
                    "position": pos,
                    "gold": gold,
                    "top5": top,
                    "in_top5": in5,
                    "in_top1": in1,
                }
            )
            built += 1
        if built >= 10:
            break

    by_len: dict[int, dict] = {}
    for row in part_b:
        L = row["length"]
        by_len.setdefault(L, {"n": 0, "top5": 0, "top1": 0})
        by_len[L]["n"] += 1
        by_len[L]["top5"] += int(row["in_top5"])
        by_len[L]["top1"] += int(row["in_top1"])

    # Recommend: longest length that keeps top5 rate high
    recommend = 1500
    for L in sorted(by_len):
        stats = by_len[L]
        rate = stats["top5"] / max(1, stats["n"])
        if rate >= 0.5:
            recommend = L
    log(f"[b] by_length={by_len} recommend_facts_chars={recommend}")

    out = {
        "part_a": {
            "match": match,
            "total": 85,
            "differ": part_a,
        },
        "part_b": {
            "rows": part_b,
            "by_length": by_len,
            "recommend_facts_chars": recommend,
        },
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    log(f"[m3-measure] wrote {OUT}")
    log("[m3-measure] done")


if __name__ == "__main__":
    asyncio.run(main())
