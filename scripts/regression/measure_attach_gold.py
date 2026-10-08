#!/usr/bin/env python3
"""Gold-hit measurement for attached-document retrieval (M3 follow-up).

Progress: /tmp/lawshift_m3_gold_prog.txt
Results:  /tmp/lawshift_m3_gold_out.json
Synthetic docs: /tmp/lawshift_m3_fir_docs/ (never logged)
Hard timeout: REGRESSION_TIMEOUT_SEC (default 1800).
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REG = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

PROG = Path("/tmp/lawshift_m3_gold_prog.txt")
OUT = Path("/tmp/lawshift_m3_gold_out.json")
DOC_DIR = Path("/tmp/lawshift_m3_fir_docs")
HARD = int(os.environ.get("REGRESSION_TIMEOUT_SEC", "1800"))
DEADLINE = time.time() + HARD

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")

DATE_IPC = "25 June 2024"
DATE_BNS = "5 August 2024"
MARGIN = 0.10
FOLLOW = "Which section applies?"


def log(msg: str) -> None:
    with PROG.open("a", encoding="utf-8") as f:
        f.write(msg + ("\n" if not msg.endswith("\n") else ""))
    print(msg, flush=True)


def check() -> None:
    if time.time() > DEADLINE:
        raise TimeoutError("hard timeout")


def gold_ids_for_route(chunk_id: str, route: str) -> set[str]:
    """Acceptable retrieval hits for a labelled gold under IPC or BNS routing."""
    from app import mapping_lookup

    act, sec = chunk_id.split("_", 1)
    act = act.upper()
    sec = sec.upper()
    if route == "BNS":
        # BNS corpus also holds BNSS/BSA.
        return {chunk_id, f"{act}_{sec}"}
    # IPC route: map BNS → IPC; BNSS/BSA have no IPC substantive gold.
    if act != "BNS":
        return set()
    res = mapping_lookup.lookup("BNS", sec)
    if not isinstance(res, dict) or not res.get("found"):
        return set()
    out: set[str] = set()
    for pair in res.get("pairs") or []:
        ipc = pair.get("ipc") or {}
        s = str(ipc.get("section") or "").upper()
        if s:
            out.add(f"IPC_{s}")
    return out


def retrieve(text: str, route: str, k: int = 5):
    from app import stage3

    scored = stage3.cascade_search_with_scores(text, corpus_act=route, k=k)
    ids = [c.chunk_id for c, _ in scored]
    score_sorted = sorted(scored, key=lambda x: x[1], reverse=True)
    opts = stage3.detect_bifurcation(score_sorted, margin=MARGIN)
    bif_ids = [c.chunk_id for c in opts] if opts and len(opts) > 1 else []
    status = "bifurcation" if bif_ids else "mapping"
    return ids, bif_ids, status


def hit(top: list[str], golds: set[str]) -> tuple[bool, bool]:
    if not golds:
        return False, False
    in5 = any(t in golds for t in top)
    in1 = bool(top) and top[0] in golds
    return in5, in1


def bif_has_gold(bif_ids: list[str], golds: set[str]) -> bool | None:
    if not bif_ids:
        return None
    return any(b in golds for b in bif_ids)


def rates(rows: list[dict]) -> dict:
    n = len(rows)
    if n == 0:
        return {"n": 0, "top5": 0.0, "top1": 0.0, "bif_n": 0, "bif_gold": 0.0}
    top5 = sum(1 for r in rows if r["in_top5"])
    top1 = sum(1 for r in rows if r["in_top1"])
    bif = [r for r in rows if r["status"] == "bifurcation"]
    bif_g = sum(1 for r in bif if r.get("bif_has_gold"))
    return {
        "n": n,
        "top5": round(top5 / n, 4),
        "top1": round(top1 / n, 4),
        "top5_count": top5,
        "top1_count": top1,
        "bif_n": len(bif),
        "bif_gold": round(bif_g / len(bif), 4) if bif else None,
        "bif_gold_count": bif_g,
        "skipped_no_gold": sum(1 for r in rows if r.get("skipped")),
    }


def strip_gold_mentions(text: str, chunk_id: str) -> str:
    """Ensure gold section number/name do not appear in synthetic FIR text."""
    act, sec = chunk_id.split("_", 1)
    # Remove bare section numbers that match gold (word-ish boundaries).
    out = re.sub(rf"\b{re.escape(sec)}\b", "[section]", text, flags=re.I)
    out = re.sub(rf"\b{re.escape(act)}\b", "[code]", out, flags=re.I)
    return out


def build_fir(facts: str, length: int, position: str, chunk_id: str) -> str:
    header = (
        "FIRST INFORMATION REPORT (synthetic). "
        "Police Station: North Test Nagar. FIR No.: TEST/00/2024. "
        "Complainant role: resident. Accused role: neighbour. "
        "Date and time of occurrence: as stated. Place: local market road. "
    )
    procedure = (
        "The duty officer recorded this complaint, issued an acknowledgment, "
        "and noted that investigation would proceed under the applicable law. "
        "Witnesses may be examined later. This boilerplate is synthetic only. "
    )
    facts_para = f"Facts: {facts.strip()} "
    pad = (
        "Further recital concerning residence, occupation, prior complaints, "
        "and routine station procedure without naming any real person. "
    ) * 40
    if position == "start":
        body = facts_para + header + procedure + pad
    elif position == "middle":
        body = header + procedure + facts_para + pad
    else:
        body = header + procedure + pad + facts_para
    body = strip_gold_mentions(body, chunk_id)
    if len(body) < length:
        body = (body + pad)[:length]
    else:
        # Keep facts paragraph present after cut.
        if position == "start":
            body = body[:length]
            if "Facts:" not in body:
                body = (facts_para + body)[:length]
        elif position == "end":
            body = body[-length:]
            if "Facts:" not in body:
                body = (body + facts_para)[-length:]
        else:
            mid = length // 2
            body = (body[: mid - len(facts_para) // 2] + facts_para + body[mid:])[:length]
            if "Facts:" not in body:
                body = (body[: mid] + facts_para + body[mid:])[:length]
    return strip_gold_mentions(body, chunk_id)[:length]


def main() -> None:
    PROG.write_text("", encoding="utf-8")
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    log("[gold] start")

    from app import stage3
    from app.stage2 import route as route_date

    log("[gold] loading Stage 3…")
    stage3.load()
    log("[gold] ready")

    bif = json.loads((REG / "bif85_questions.json").read_text(encoding="utf-8"))
    questions = bif["questions"]

    # Resolve evaluable golds under IPC and BNS dates.
    enriched = []
    for i, q in enumerate(questions, 1):
        cid = q["chunk_id"]
        gold_ipc = gold_ids_for_route(cid, "IPC")
        gold_bns = gold_ids_for_route(cid, "BNS")
        enriched.append(
            {
                "n": i,
                "id": q["id"],
                "question": q["question"],
                "chunk_id": cid,
                "gold_ipc": sorted(gold_ipc),
                "gold_bns": sorted(gold_bns),
            }
        )

    # Part 1: 85 questions — use date matching gold act when possible.
    # Baseline bif85 used IPC date for all; here each question uses:
    #   BNS_* → BNS date; BNSS/BSA → BNS date; and we also report IPC-date
    #   baseline for those with an IPC mapping (a_ipc).
    modes_part1 = ["a", "b", "c", "d"]
    part1_rows: dict[str, list] = {m: [] for m in modes_part1}
    part1_rows["a_ipc_mapped"] = []

    for row in enriched:
        check()
        qtext = row["question"].strip()
        cid = row["chunk_id"]
        act = cid.split("_", 1)[0]
        if act == "BNS" and row["gold_bns"]:
            dlabel = DATE_BNS
            route = "BNS"
            golds = set(row["gold_bns"])
        else:
            # BNSS/BSA live in BNS-side corpus
            dlabel = DATE_BNS
            route = "BNS"
            golds = set(row["gold_bns"]) or {cid}

        texts = {
            "a": f"{qtext} {dlabel}".strip(),
            "b": qtext,
            "c": f"{FOLLOW}\n\n{qtext}",
            "d": f"{qtext}\n\n{FOLLOW}",
        }
        for mode, text in texts.items():
            top, bif_ids, status = retrieve(text, route)
            in5, in1 = hit(top, golds)
            bh = bif_has_gold(bif_ids, golds)
            part1_rows[mode].append(
                {
                    "n": row["n"],
                    "id": row["id"],
                    "route": route,
                    "gold": sorted(golds),
                    "top5": top,
                    "status": status,
                    "in_top5": in5,
                    "in_top1": in1,
                    "bif_has_gold": bh,
                }
            )

        # Extra: IPC-date baseline when mapping exists (classic bif85 date).
        if row["gold_ipc"]:
            text = f"{qtext} {DATE_IPC}".strip()
            top, bif_ids, status = retrieve(text, "IPC")
            in5, in1 = hit(top, set(row["gold_ipc"]))
            part1_rows["a_ipc_mapped"].append(
                {
                    "n": row["n"],
                    "in_top5": in5,
                    "in_top1": in1,
                    "status": status,
                    "bif_has_gold": bif_has_gold(bif_ids, set(row["gold_ipc"])),
                }
            )

        if row["n"] % 10 == 0:
            log(f"[part1] {row['n']}/85")

    part1_summary = {m: rates(part1_rows[m]) for m in part1_rows}
    log(f"[part1] summary {json.dumps(part1_summary)}")

    # Part 2: 40 questions — 20 IPC-mapped + 20 BNS, FIR wrappers.
    ipc_pool = [r for r in enriched if r["gold_ipc"] and r["chunk_id"].startswith("BNS_")]
    bns_pool = [r for r in enriched if r["chunk_id"].startswith("BNS_") and r["gold_bns"]]
    # Prefer distinct questions
    ipc_sel = ipc_pool[:20]
    bns_sel = [r for r in bns_pool if r not in ipc_sel][:20]
    if len(bns_sel) < 20:
        bns_sel = bns_pool[:20]
    selected = [("IPC", DATE_IPC, r) for r in ipc_sel] + [
        ("BNS", DATE_BNS, r) for r in bns_sel
    ]
    log(f"[part2] selected ipc={len(ipc_sel)} bns={len(bns_sel)}")

    lengths = [800, 1500, 3000, 6000]
    positions = ["start", "middle", "end"]
    # modes: c (follow-up first), b (facts only), first500
    part2_rows = []
    doc_index = []
    for route, dlabel, row in selected:
        check()
        golds = set(row["gold_ipc"] if route == "IPC" else row["gold_bns"])
        facts = row["question"].strip()
        for L in lengths:
            for pos in positions:
                fir = build_fir(facts, L, pos, row["chunk_id"])
                # Never write gold section into filename content; path only.
                fname = f"{row['id']}_{route}_{L}_{pos}.txt"
                (DOC_DIR / fname).write_text(fir, encoding="utf-8")
                doc_index.append({"file": fname, "n": row["n"], "route": route, "L": L, "pos": pos})

                variants = {
                    "b": fir,
                    "c": f"{FOLLOW}\n\n{fir}",
                    "first500": fir[:500],
                }
                for mode, text in variants.items():
                    top, bif_ids, status = retrieve(text, route)
                    in5, in1 = hit(top, golds)
                    part2_rows.append(
                        {
                            "n": row["n"],
                            "id": row["id"],
                            "route": route,
                            "length": L,
                            "position": pos,
                            "mode": mode,
                            "in_top5": in5,
                            "in_top1": in1,
                            "status": status,
                            "top0": top[0] if top else None,
                        }
                    )
        if row["n"] % 5 == 0:
            log(f"[part2] done question n={row['n']}")

    # Aggregate part2
    def agg(filter_fn):
        sub = [r for r in part2_rows if filter_fn(r)]
        return {
            "n": len(sub),
            "top5_count": sum(1 for r in sub if r["in_top5"]),
            "top1_count": sum(1 for r in sub if r["in_top1"]),
            "top5": round(sum(1 for r in sub if r["in_top5"]) / len(sub), 4) if sub else 0.0,
            "top1": round(sum(1 for r in sub if r["in_top1"]) / len(sub), 4) if sub else 0.0,
        }

    part2_by = {
        "by_mode": {m: agg(lambda r, m=m: r["mode"] == m) for m in ("b", "c", "first500")},
        "by_length_mode": {},
        "by_position_mode": {},
    }
    for L in lengths:
        for m in ("b", "c", "first500"):
            part2_by["by_length_mode"][f"{L}:{m}"] = agg(
                lambda r, L=L, m=m: r["length"] == L and r["mode"] == m
            )
    for pos in positions:
        for m in ("b", "c", "first500"):
            part2_by["by_position_mode"][f"{pos}:{m}"] = agg(
                lambda r, pos=pos, m=m: r["position"] == pos and r["mode"] == m
            )

    log(f"[part2] by_mode {json.dumps(part2_by['by_mode'])}")

    # Truncation sweep on mode b: facts truncated to N chars (plain questions)
    trunc_rows = {}
    for N in (300, 500, 800, 1200, 2000, None):
        rows = []
        for row in enriched:
            if not row["gold_bns"] and not row["gold_ipc"]:
                continue
            act = row["chunk_id"].split("_", 1)[0]
            route = "BNS"
            golds = set(row["gold_bns"]) or {row["chunk_id"]}
            text = row["question"] if N is None else row["question"][:N]
            # For FIR-like: use a 3000-char start-position FIR truncated
            fir = build_fir(row["question"], 3000, "start", row["chunk_id"])
            text = fir if N is None else fir[:N]
            top, bif_ids, status = retrieve(text, route)
            in5, in1 = hit(top, golds)
            rows.append({"in_top5": in5, "in_top1": in1, "status": status, "bif_has_gold": bif_has_gold(bif_ids, golds)})
        key = "full" if N is None else str(N)
        trunc_rows[key] = rates(rows)
        log(f"[trunc] N={key} {trunc_rows[key]}")

    out = {
        "part1_summary": part1_summary,
        "part2_summary": part2_by,
        "truncation_sweep_fir3000_start": trunc_rows,
        "doc_dir": str(DOC_DIR),
        "doc_count": len(doc_index),
        "selected_ipc_n": [r["n"] for r in ipc_sel],
        "selected_bns_n": [r["n"] for r in bns_sel],
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    (DOC_DIR / "index.json").write_text(json.dumps(doc_index, indent=2), encoding="utf-8")
    log(f"[gold] wrote {OUT}")
    log("[gold] done")


if __name__ == "__main__":
    main()
