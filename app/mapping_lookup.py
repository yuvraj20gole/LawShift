"""Read-only IPC <-> BNS lookup over data/clean/mapping.jsonl.

No model calls, no accounts. Reads the mapping table plus the statute files
already in the project:
  - data/clean/mapping.jsonl   (562 rows: ipc_section, bns_section, mapping_type, ...)
  - data/clean/statutes.jsonl  (BNS section titles, for suggestions and for
                                BNS sections the mapping table never mentions)

The mapping table's own `mapping_type` values are passed through unchanged:
section | partial | merged | dropped.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / "data" / "clean" / "mapping.jsonl"
STATUTES_PATH = ROOT / "data" / "clean" / "statutes.jsonl"

_BASE_RE = re.compile(r"^\s*(\d+[A-Za-z]{0,2})")


def _natural_key(section: str):
    m = re.match(r"^(\d+)([A-Za-z]*)", section)
    return (int(m.group(1)), m.group(2)) if m else (10**9, section)


def clean_ipc_text(raw: str) -> str:
    """Drop the dataset's header, state amendments and footnote markers."""
    t = raw or ""
    t = re.sub(r"^\s*Indian Penal Code,\s*1860\s*", "", t)
    cut = re.search(r"STATE AMENDMENTS?", t)
    if cut:
        t = t[: cut.start()]
    t = re.sub(r"\b\d{1,3}\s{0,3}\[", "", t)  # "138 [" footnote markers
    t = t.replace("[", "").replace("]", "")
    t = re.sub(r"\(\s*(\w+)\s*\)", r"(\1)", t)
    return re.sub(r"\s+", " ", t).strip()


def _bns_title(text: str, fallback: str) -> str:
    """statutes.jsonl truncates long section_title values; the statute text has the full one."""
    m = re.search(r"\]\s*\d+[A-Za-z]{0,2}\.\s*(.+?)\.\s*[\u2014\u2013-]", text or "", flags=re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else (fallback or "")


def clean_bns_text(raw: str) -> str:
    t = re.sub(r"^\s*The Bharatiya Nyaya Sanhita,\s*2023\s*", "", raw or "")
    return re.sub(r"\s+", " ", t).strip()


@lru_cache(maxsize=1)
def _load():
    rows = []
    if MAPPING_PATH.is_file():
        for line in MAPPING_PATH.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))

    ipc_index: dict[str, list[dict]] = {}
    bns_index: dict[str, list[dict]] = {}  # reverse index: BNS base section -> mapping rows
    for r in rows:
        ipc_index.setdefault(str(r["ipc_section"]).upper(), []).append(r)
        base = r.get("bns_base_section")
        if base and r.get("mapping_type") != "dropped":
            bns_index.setdefault(str(base).upper(), []).append(r)

    bns_titles: dict[str, str] = {}
    bns_texts: dict[str, str] = {}
    if STATUTES_PATH.is_file():
        for line in STATUTES_PATH.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            cid = str(d.get("chunk_id", ""))
            if cid.startswith("BNS_"):
                sec = str(d.get("section_number") or cid[4:]).upper()
                bns_texts[sec] = d.get("text") or ""
                bns_titles[sec] = _bns_title(bns_texts[sec], d.get("section_title") or "")
    return rows, ipc_index, bns_index, bns_titles, bns_texts


def sections(code: str) -> list[dict]:
    rows, _, _, bns_titles, _ = _load()
    if code == "IPC":
        seen: dict[str, str] = {}
        for r in rows:
            seen.setdefault(str(r["ipc_section"]), r.get("ipc_heading") or "")
        out = [{"section": s, "title": t} for s, t in seen.items()]
    else:
        out = [{"section": s, "title": t} for s, t in bns_titles.items()]
    return sorted(out, key=lambda x: _natural_key(x["section"]))


def _ipc_card(r: dict) -> dict:
    return {
        "code": "IPC",
        "section": str(r["ipc_section"]),
        "heading": r.get("ipc_heading") or "",
        "text": clean_ipc_text(r.get("ipc_description", "")),
    }


def _bns_card(r: dict) -> dict:
    return {
        "code": "BNS",
        "section": str(r.get("bns_section")),
        "base": r.get("bns_base_section"),
        "subclauses": r.get("bns_subclauses") or [],
        "heading": r.get("bns_heading") or "",
        "text": clean_bns_text(r.get("bns_description", "")),
    }


def lookup(code: str, section: str) -> dict:
    rows, ipc_index, bns_index, bns_titles, bns_texts = _load()
    sec = (section or "").strip()
    key = sec.upper()
    pairs: list[dict] = []
    found = False
    title = ""

    if code == "IPC":
        for r in ipc_index.get(key, []):
            found = True
            title = r.get("ipc_heading") or title
            pairs.append(
                {
                    "mappingType": r.get("mapping_type"),
                    "ipc": _ipc_card(r),
                    "bns": None if r.get("mapping_type") == "dropped" else _bns_card(r),
                    "datasetEntry": r.get("raw"),
                    "bnsNote": r.get("bns_note"),
                }
            )
    else:
        # "193(1)" -> exact sub-clause rows first, else every row for base 193
        base_m = re.match(r"^\s*(\d+[A-Za-z]{0,2})", sec)
        base = base_m.group(1).upper() if base_m else key
        cands = bns_index.get(base, [])
        exact = [r for r in cands if str(r.get("bns_section", "")).upper().replace(" ", "") == key.replace(" ", "")]
        for r in exact or cands:
            pairs.append(
                {
                    "mappingType": r.get("mapping_type"),
                    "ipc": _ipc_card(r),
                    "bns": _bns_card(r),
                    "datasetEntry": r.get("raw"),
                    "bnsNote": r.get("bns_note"),
                }
            )
        if base in bns_titles or pairs:
            found = True
            title = bns_titles.get(base, "")

    result = {
        "code": code,
        "section": sec,
        "found": found,
        "title": title,
        "pairs": pairs,
        "matchCount": len(pairs),
    }
    # A BNS section that exists but has no row in the table: return its own card only.
    if code == "BNS" and found and not pairs:
        base_m = re.match(r"^\s*(\d+[A-Za-z]{0,2})", sec)
        base = base_m.group(1).upper() if base_m else key
        result["bnsOnly"] = {
            "code": "BNS",
            "section": base,
            "heading": bns_titles.get(base, ""),
            "text": clean_bns_text(re.sub(r"^\[Context:[^\]]*\]\s*", "", bns_texts.get(base, ""))),
        }
    return result
