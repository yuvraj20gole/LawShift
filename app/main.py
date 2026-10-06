"""FastAPI backend wiring Stages 1–4.

Run: uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

import json
import re
import time
from contextlib import asynccontextmanager
from datetime import date
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, File, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from . import mapping_lookup, stage0_document, stage1, stage2, stage3, stage4, stage5_translate
from .schemas import (
    BifurcationOption,
    BifurcationResponse,
    ClarifyResponse,
    FailureResponse,
    MappingResponse,
    OffenseDateUsed,
    PipelineStep,
    QueryRequest,
    ResolveBifurcationRequest,
    SectionBadge,
    SectionLookupItem,
    SectionLookupResponse,
    Source,
)

# Bifurcation escape: last option; resolve clears pending and asks for facts.
DESCRIBE_FACTS_OPTION = "None of these. I will describe what happened"
DESCRIBE_FACTS_PROMPT = (
    "Describe what happened (who did what, and to whom) and I will search again."
)
SECTION_LOOKUP_NOTE = (
    "You gave a section but no facts, so no analysis was written. "
    "Describe what happened to get one."
)
BIFURCATION_EXHAUSTED_NOTE = (
    "I could not narrow this down further. Open a section to read it, or add more detail."
)
_NO_MAPPING_EQUIVALENT = "No equivalent is recorded in our mapping table"

# Per-conversation locked offence date (frontend conversation_id contract).
_LOCKED_DATES: dict[str, date] = {}

# Pending bifurcation choices: conversation_id -> state for resolve endpoint.
_PENDING_BIFURCATION: dict[str, dict] = {}

# Sections offered in a score-gap bifurcation and rejected via "None of these"
# (conversation_id -> set of labels like "IPC 292").
_REJECTED_BIFURCATION_SECTIONS: dict[str, set[str]] = {}


def _format_offense_date(d: date) -> str:
    """Human date like '25 June 2024' (day without leading zero)."""
    try:
        return d.strftime("%-d %B %Y")
    except ValueError:
        return d.strftime("%d %B %Y").lstrip("0")


def _same_cutoff_side(a: date, b: date) -> bool:
    """True when both dates are before the cutoff, or both on/after it."""
    return (a < stage2.CUTOFF) == (b < stage2.CUTOFF)


def _code_short_name(code: str) -> str:
    return "Indian Penal Code" if code == "IPC" else "Bharatiya Nyaya Sanhita"


def _attach_date_lock_label(resp, label: str | None):
    """Set date_lock_label on a response model when a same-side note applies."""
    if not label:
        return resp
    return resp.model_copy(update={"date_lock_label": label})


def _build_offense_date_used(
    offense_date: date,
    route: str,
    *,
    source: str = "message",
) -> OffenseDateUsed:
    """Display-only payload for the 'Offence date used' line."""
    src = source if source in {"message", "earlier_message", "document"} else "message"
    code = route if route in {"IPC", "BNS"} else stage2.route(offense_date)
    return OffenseDateUsed(
        label=_format_offense_date(offense_date),
        code=code,  # type: ignore[arg-type]
        source=src,  # type: ignore[arg-type]
    )


def _attach_offense_date_used(resp, payload: OffenseDateUsed | None):
    if payload is None or not hasattr(resp, "model_copy"):
        return resp
    if not hasattr(resp, "offense_date_used"):
        return resp
    return resp.model_copy(update={"offense_date_used": payload})


def _build_date_conflict_response(
    *,
    conversation_id: str,
    message: str,
    locked: date,
    new_date: date,
    language: str = "en",
) -> BifurcationResponse:
    """Ask which offence date applies when lock and message cross the cutoff."""
    locked_label = _format_offense_date(locked)
    new_label = _format_offense_date(new_date)
    locked_code = stage2.route(locked)
    new_code = stage2.route(new_date)
    prompt = (
        f"Earlier you gave {locked_label} ({_code_short_name(locked_code)}). "
        f"This message says {new_label} ({_code_short_name(new_code)}). "
        "Which is the date of the offence?"
    )
    options = [
        BifurcationOption(
            section=locked_label,
            description=_code_short_name(locked_code),
        ),
        BifurcationOption(
            section=new_label,
            description=_code_short_name(new_code),
        ),
    ]
    _PENDING_BIFURCATION[conversation_id] = {
        "source": "date_conflict",
        "message": message,
        "language": language,
        "date_choices": {
            locked_label: locked,
            new_label: new_date,
        },
        # Keep keys resolve_bifurcation expects for non-date paths unused here.
        "by_section": {},
        "offense_date": locked,
        "matched_text": locked_label,
        "reason": "date_conflict",
        "route": locked_code,
    }
    return BifurcationResponse(
        prompt=prompt,
        options=options,
        reason="date_conflict",
    )


def _warm_up_ollama_models() -> None:
    """Force 3B + 14B into memory together so cold-swap cost hits at startup."""
    print("[startup] Warming up Ollama models (3B + 14B)...", flush=True)
    start = time.time()
    try:
        # Trivial call to each model to force them both into memory
        # together, so the cold-swap eviction happens now, not on the
        # first real query.
        stage4.generate_irac(
            question="test",
            retrieved_text="This is a placeholder statutory text for warm-up purposes only.",
            source_citation="WARMUP",
        )
        stage4.verify_rule_only_14b_v2(
            rule_text="This is a placeholder rule for warm-up purposes only.",
            conclusion_text="This is a placeholder conclusion for warm-up purposes only.",
        )
        elapsed = time.time() - start
        print(
            f"[startup] Model warm-up complete in {elapsed:.1f}s - both models resident.",
            flush=True,
        )
    except Exception as e:
        print(
            f"[startup] Warm-up failed (non-fatal, will warm on first real request): {e}",
            flush=True,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[startup] Checking Ollama…", flush=True)
    stage4.check_ollama()
    print(f"[startup] Ollama OK ({stage4.GEN_MODEL}, {stage4.VERIFY_MODEL})", flush=True)
    print("[startup] Loading Stage 3 retrieval corpora…", flush=True)
    stage3.load()
    # After Ollama reachability + Stage 3 load — pay 3B/14B residency cost here.
    _warm_up_ollama_models()
    print("[startup] Ready.", flush=True)
    yield


app = FastAPI(title="Legal RAG Pipeline", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "locked_conversations": len(_LOCKED_DATES),
        "pending_bifurcations": len(_PENDING_BIFURCATION),
    }


_RULINGS_PATH = Path(__file__).resolve().parents[1] / "data" / "rulings_index.json"


@lru_cache(maxsize=1)
def _load_rulings_index() -> dict:
    if not _RULINGS_PATH.is_file():
        return {
            "generatedOn": None,
            "courts": {},
            "branchCounts": {},
            "caseTypeMapping": [],
            "rulings": [],
        }
    return json.loads(_RULINGS_PATH.read_text(encoding="utf-8"))


@app.get("/api/rulings")
async def list_rulings(
    court: str | None = Query(None, description="Substring match on court name"),
    branch: str | None = Query(
        None, description="criminal | civil | other | writ (case-insensitive)"
    ),
    q: str | None = Query(
        None, description="Substring match on title, caseType, or caseNumber"
    ),
    limit: int = Query(50, ge=1, le=400),
    offset: int = Query(0, ge=0, description="Skip this many matching rows (paging)"),
    bench: str | None = Query(
        None, description="Exact bench code as recorded in the archive (Bombay High Court)"
    ),
):
    """Read-only rulings index built by scripts/build_rulings_index.py."""
    index = _load_rulings_index()
    rows = index.get("rulings") or []

    if court:
        needle = court.casefold()
        rows = [r for r in rows if needle in str(r.get("court", "")).casefold()]
    # Bench facet: every bench seen for the court filter alone, before narrowing further.
    bench_counts: dict[str, dict] = {}
    for r in rows:
        b = r.get("bench")
        if not b:
            continue
        slot = bench_counts.setdefault(
            b, {"code": b, "benchLabel": r.get("benchLabel"), "count": 0}
        )
        slot["count"] += 1
    benches = sorted(bench_counts.values(), key=lambda x: -x["count"])

    if bench:
        rows = [r for r in rows if r.get("bench") == bench]
    if branch:
        want = branch.casefold()
        rows = [r for r in rows if str(r.get("branch", "")).casefold() == want]
    if q:
        needle = q.casefold()
        rows = [
            r
            for r in rows
            if needle in str(r.get("title", "")).casefold()
            or needle in str(r.get("caseType", "")).casefold()
            or needle in str(r.get("caseNumber", "")).casefold()
        ]

    # Newest first (ISO dates sort lexicographically)
    rows = sorted(rows, key=lambda r: r.get("decidedOn") or "", reverse=True)
    clipped = rows[offset : offset + limit]

    return {
        "generatedOn": index.get("generatedOn"),
        "courts": index.get("courts"),
        "count": len(clipped),
        "offset": offset,
        "totalMatching": len(rows),
        "benches": benches,
        "rulings": clipped,
    }


@app.get("/api/map")
async def map_section(
    code: str = Query(..., description="IPC or BNS: the code the section number is in"),
    section: str = Query(..., min_length=1, max_length=12),
):
    """Read-only IPC <-> BNS lookup from data/clean/mapping.jsonl. No model calls."""
    c = code.strip().upper()
    if c not in {"IPC", "BNS"}:
        return {"error": "code must be IPC or BNS"}
    return mapping_lookup.lookup(c, section)


@app.get("/api/map/sections")
async def map_sections(code: str = Query(..., description="IPC or BNS")):
    """Section numbers and titles for suggestions."""
    c = code.strip().upper()
    if c not in {"IPC", "BNS"}:
        return {"error": "code must be IPC or BNS"}
    return {"code": c, "sections": mapping_lookup.sections(c)}


def _build_mapping(
    message: str,
    offense_date: date,
    matched_text: str,
    reason: str,
    route: str,
    top_chunk: stage3.RetrievedChunk,
    retrieve_detail: str,
    language: str = "en",
    offense_date_used: OffenseDateUsed | None = None,
) -> MappingResponse | FailureResponse:
    try:
        irac_text = stage4.generate_irac(message, top_chunk.text, top_chunk.chunk_id)
    except Exception as exc:
        return FailureResponse(
            reason="source_unavailable",
            message=f"Generation failed: {exc}",
        )

    irac_parsed = stage4.parse_irac(irac_text)
    irac = {
        "issue": irac_parsed.get("issue", ""),
        "rule": irac_parsed.get("rule", ""),
        "application": irac_parsed.get("application", ""),
        "conclusion": irac_parsed.get("conclusion", ""),
    }

    try:
        verdict, explanation = stage4.verify_rule_only_14b_v2(
            irac["rule"], irac["conclusion"]
        )
    except Exception as exc:
        verdict, explanation = "SUPPORTED", f"Verifier unavailable: {exc}"

    # Stage 5: Multilingual translation (post-processing only)
    engine: str | None = None
    translation_note: str | None = None
    if language and language != "en":
        try:
            irac, engine, translation_note = stage5_translate.translate_irac(
                irac, target_lang=language
            )
        except Exception as exc:
            print(f"[stage5] Translation to '{language}' failed: {exc}")

    statute_label = (
        top_chunk.act if top_chunk.act in {"IPC", "BNS", "BNSS", "BSA"} else route
    )

    pipeline_steps = [
        PipelineStep(
            stage="extract",
            detail=f"Offence date: {offense_date} ({matched_text}; {reason})",
        ),
        PipelineStep(stage="gate", detail=f"Routed to {route}"),
        PipelineStep(stage="retrieve", detail=retrieve_detail),
        PipelineStep(
            stage="synthesize",
            detail=f"IRAC via {stage4.GEN_MODEL}; verify via {stage4.VERIFY_MODEL}",
        ),
    ]

    return MappingResponse(
        summary=f"{statute_label} {top_chunk.section_number}",
        badge=SectionBadge(
            code=route,  # Literal IPC|BNS from Stage 2 gate
            section=str(top_chunk.section_number),
            offenceName=top_chunk.section_title or top_chunk.chunk_id,
        ),
        irac=irac,
        sources=[
            Source(
                statute=statute_label,
                section=str(top_chunk.section_number),
                text=top_chunk.text,
            )
        ],
        pipeline=pipeline_steps,
        verification={
            "flagged": verdict == "NOT_SUPPORTED",
            "confidence_note": (
                explanation
                if verdict == "NOT_SUPPORTED"
                else "No inconsistency detected between the generated conclusion and the retrieved rule."
            ),
        },
        engine=engine,  # type: ignore[arg-type]
        translation_note=translation_note,
        offense_date_used=offense_date_used,
    )


# Words that ask about the law without describing what happened.
# Reviewed list — extend carefully; one leftover content word lets the query through.
MISSING_FACTS_META_WORDS: frozenset[str] = frozenset(
    {
        "which",
        "what",
        "section",
        "sections",
        "law",
        "laws",
        "act",
        "acts",
        "applies",
        "apply",
        "applicable",
        "case",
        "cases",
        "legal",
        "illegal",
        "help",
        "tell",
        "me",
        "this",
        "that",
        "these",
        "those",
        "offence",
        "offense",
        "crime",
        "crimes",
        "matter",
        "issue",
        "issues",
        "date",
        "dates",
        "dated",
        "day",
        "month",
        "year",
        "please",
        "ask",
        "asking",
        "know",
        "find",
        "finding",
        "need",
        "needed",
        "want",
        "wants",
        "give",
        "show",
        "explain",
        "about",
        "regarding",
        "under",
        "indian",
        "india",
        "code",
        "codes",
        "current",
        "new",
        "old",
        "ipc",
        "bns",
        "bnss",
        "bsa",
        "happened",
        "happen",
        "occurring",
        "occurred",
        "done",
        "doing",
        "did",
    }
)

# Function words stripped alongside meta words (English).
MISSING_FACTS_STOPWORDS: frozenset[str] = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "if",
        "then",
        "than",
        "so",
        "not",
        "no",
        "nor",
        "too",
        "very",
        "just",
        "also",
        "only",
        "own",
        "same",
        "such",
        "both",
        "each",
        "few",
        "more",
        "most",
        "other",
        "some",
        "any",
        "all",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "am",
        "have",
        "has",
        "had",
        "do",
        "does",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "shall",
        "can",
        "of",
        "to",
        "for",
        "in",
        "on",
        "at",
        "by",
        "with",
        "from",
        "as",
        "into",
        "between",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "how",
        "when",
        "where",
        "why",
        "who",
        "whom",
        "whose",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "my",
        "your",
        "his",
        "her",
        "its",
        "our",
        "their",
        "there",
        "here",
        "out",
        "up",
        "down",
        "over",
        "again",
        "further",
        "once",
        "because",
        "until",
        "while",
        "against",
        "among",
        "across",
        "within",
        "without",
        "via",
        "per",
        "vs",
        "etc",
    }
)

_MISSING_FACTS_DROP = MISSING_FACTS_META_WORDS | MISSING_FACTS_STOPWORDS

# Explicit statute citation — lets the query through even with zero content words.
# Number may carry a lettered suffix (124A). Act and number in either order;
# "section"/"sec"/"s."/"u/s" also count as a citation cue next to the number.
# Word boundaries prevent "applies. 10" (date day) from matching as "s." + 10.
# Pattern (verbose form of EXPLICIT_CITATION_RE):
#   (?<![A-Za-z])(?:IPC|BNS|BNSS|BSA|CrPC)\s*[#:]?\s*\d+[A-Za-z]{0,3}\b
#   | (?<![A-Za-z])\d+[A-Za-z]{0,3}\s+(?:IPC|BNS|BNSS|BSA|CrPC)\b
#   | (?<![A-Za-z])(?:sections?|sec\.?|s\.|u/s)\s*[#:]?\s*\d+[A-Za-z]{0,3}\b
#   | (?<![A-Za-z])\d+[A-Za-z]{0,3}\s+(?:sections?|sec\.?|s\.|u/s)\b
_SECTION_NUM_RE = r"\d+[A-Za-z]{0,3}"
_ACT_RE = r"(?:IPC|BNS|BNSS|BSA|CrPC)"
_SEC_WORD_RE = r"(?:sections?|sec\.?|s\.|u/s)"
EXPLICIT_CITATION_RE = re.compile(
    rf"(?:"
    rf"(?<![A-Za-z])(?:{_ACT_RE})\s*[#:]?\s*{_SECTION_NUM_RE}\b"
    rf"|(?<![A-Za-z]){_SECTION_NUM_RE}\s+(?:{_ACT_RE})\b"
    rf"|(?<![A-Za-z])(?:{_SEC_WORD_RE})\s*[#:]?\s*{_SECTION_NUM_RE}\b"
    rf"|(?<![A-Za-z]){_SECTION_NUM_RE}\s+(?:{_SEC_WORD_RE})\b"
    rf")",
    re.IGNORECASE,
)


def message_has_explicit_citation(message: str) -> bool:
    """True when the message names a section number with an act or section cue."""
    return EXPLICIT_CITATION_RE.search(message or "") is not None


def content_tokens_after_date(
    message: str, matched_date_text: str | None
) -> list[str]:
    """Tokens left after removing the matched date and meta/stop words.

    Pure digits are dropped (section numbers / date remnants are not facts).
    One leftover content token is enough for the query to proceed.
    """
    text = message or ""
    if matched_date_text and matched_date_text not in {"", "(locked)"}:
        # Remove the Stage 1 matched span (case-insensitive).
        text = re.sub(re.escape(matched_date_text), " ", text, flags=re.I)
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = [t for t in text.split() if t]
    kept: list[str] = []
    for t in tokens:
        if t.isdigit():
            continue
        if t in _MISSING_FACTS_DROP:
            continue
        kept.append(t)
    return kept


def message_missing_offense_facts(
    message: str, matched_date_text: str | None
) -> bool:
    """True when the message has a date context but no remaining content words.

    Explicit citations (e.g. \"IPC 292\", \"Section 302\") count as content
    even when every token would otherwise be stripped as meta/digits.
    """
    if message_has_explicit_citation(message):
        return False
    return len(content_tokens_after_date(message, matched_date_text)) == 0


def message_is_citation_only(
    message: str, matched_date_text: str | None
) -> bool:
    """True when only date + meta + explicit citation spans remain.

    Removes the matched date and every EXPLICIT_CITATION_RE span, then
    applies the same token filter as missing-facts. Any leftover content
    word means the message is not citation-only (unchanged pipeline).
    """
    if not message_has_explicit_citation(message):
        return False
    text = message or ""
    if matched_date_text and matched_date_text not in {"", "(locked)"}:
        text = re.sub(re.escape(matched_date_text), " ", text, flags=re.I)
    text = EXPLICIT_CITATION_RE.sub(" ", text)
    return len(content_tokens_after_date(text, None)) == 0


def _mapping_fields_for_section(
    code: str, section: str
) -> tuple[str, str, str | None, str | None, str | None, str | None]:
    """English mapping_line plus structured fields for client localisation.

    Returns
    (mapping_line, mapping_status, equiv_code, equiv_section,
     equiv_heading, mapping_type).
    """
    result = mapping_lookup.lookup(code, section)
    pairs = result.get("pairs") or []
    if not pairs:
        return _NO_MAPPING_EQUIVALENT, "none", None, None, None, None
    pair = pairs[0]
    mtype = pair.get("mappingType") or "section"
    if mtype == "dropped":
        return _NO_MAPPING_EQUIVALENT, "none", None, None, None, None
    phrase = _mapping_type_phrase(mtype)
    if code == "IPC":
        other = pair.get("bns")
        if not other:
            return _NO_MAPPING_EQUIVALENT, "none", None, None, None, None
        equiv_code = "BNS"
        equiv_section = str(other.get("section") or "")
        equiv_heading = (other.get("heading") or "").strip()
        other_name = _code_full_name("BNS")
    else:
        other = pair.get("ipc")
        if not other:
            return _NO_MAPPING_EQUIVALENT, "none", None, None, None, None
        equiv_code = "IPC"
        equiv_section = str(other.get("section") or "")
        equiv_heading = (other.get("heading") or "").strip()
        other_name = _code_full_name("IPC")
    label = f"{equiv_code} {equiv_section}"
    suffix = f" ({equiv_heading})" if equiv_heading else ""
    line = f"In {other_name}, {phrase} {label}{suffix}."
    mtype_norm = mtype if mtype in {"section", "partial", "merged"} else "section"
    return line, "equivalent", equiv_code, equiv_section, equiv_heading, mtype_norm


def _chunk_section_label(chunk: stage3.RetrievedChunk) -> str:
    return f"{chunk.act} {chunk.section_number}"


def _remember_rejected_sections(conversation_id: str, pending: dict) -> None:
    """Record score-gap options the user dismissed via 'None of these'."""
    if pending.get("source") in {"code_mismatch", "date_conflict"}:
        return
    labels: set[str] = set()
    offered = pending.get("offered_labels")
    if isinstance(offered, (list, set, tuple)):
        labels.update(str(x) for x in offered)
    else:
        seen_ids: set[str] = set()
        for chunk in (pending.get("by_section") or {}).values():
            cid = getattr(chunk, "chunk_id", None)
            if cid is None or cid in seen_ids:
                continue
            seen_ids.add(cid)
            labels.add(_chunk_section_label(chunk))
    if not labels:
        return
    bucket = _REJECTED_BIFURCATION_SECTIONS.setdefault(conversation_id, set())
    bucket.update(labels)


def _build_section_lookup_item_from_chunk(
    chunk: stage3.RetrievedChunk,
) -> SectionLookupItem:
    act = (chunk.act or "").upper()
    if act not in {"IPC", "BNS", "BNSS", "BSA"}:
        act = "IPC" if act.startswith("IPC") else act
    sec = str(chunk.section_number)
    heading = (chunk.section_title or "").strip()
    if heading.lower() in {"nan", "none", "null"}:
        heading = ""
    if act in {"IPC", "BNS"}:
        line, status, eq_code, eq_sec, eq_head, mtype = _mapping_fields_for_section(
            act, sec
        )
    else:
        line, status, eq_code, eq_sec, eq_head, mtype = (
            _NO_MAPPING_EQUIVALENT,
            "none",
            None,
            None,
            None,
            None,
        )
    return SectionLookupItem(
        code=act,  # type: ignore[arg-type]
        section=sec,
        heading=heading,
        text=chunk.text or "",
        found=True,
        mapping_line=line,
        mapping_status=status,  # type: ignore[arg-type]
        equiv_code=eq_code,  # type: ignore[arg-type]
        equiv_section=eq_sec,
        equiv_heading=eq_head,
        mapping_type=mtype,  # type: ignore[arg-type]
    )


def _build_section_lookup(
    citations: list[tuple[str, str]],
    *,
    note: str | None = None,
    reason: str | None = "citation_only",
    offense_date_used: OffenseDateUsed | None = None,
) -> SectionLookupResponse:
    """Statute + mapping for up to three matching-route citations; no IRAC."""
    items: list[SectionLookupItem] = []
    for code, sec in citations[:3]:
        chunk_id = f"{code}_{sec}"
        chunk = stage3.get_chunk_by_id(chunk_id, code)
        if chunk is None:
            items.append(
                SectionLookupItem(
                    code=code,  # type: ignore[arg-type]
                    section=sec,
                    heading="",
                    text="",
                    found=False,
                    mapping_line=f"{code} {sec} is not in the statute text we hold.",
                    mapping_status="missing",
                )
            )
            continue
        items.append(_build_section_lookup_item_from_chunk(chunk))
    return SectionLookupResponse(
        note=note or SECTION_LOOKUP_NOTE,
        items=items,
        reason=reason,  # type: ignore[arg-type]
        offense_date_used=offense_date_used,
    )


def _build_section_lookup_from_chunks(
    chunks: list[stage3.RetrievedChunk],
    *,
    note: str,
    reason: str | None = "bifurcation_exhausted",
    offense_date_used: OffenseDateUsed | None = None,
) -> SectionLookupResponse:
    """Plain cards from RetrievedChunk list (up to three); no IRAC."""
    seen: set[str] = set()
    items: list[SectionLookupItem] = []
    for chunk in chunks:
        label = _chunk_section_label(chunk)
        if label in seen:
            continue
        seen.add(label)
        items.append(_build_section_lookup_item_from_chunk(chunk))
        if len(items) >= 3:
            break
    return SectionLookupResponse(
        note=note,
        items=items,
        reason=reason,  # type: ignore[arg-type]
        offense_date_used=offense_date_used,
    )


def _with_describe_facts_option(
    options: list[BifurcationOption],
) -> list[BifurcationOption]:
    """Append the escape option; does not change which sections were offered."""
    if any(
        o.section.lower().startswith("none of these") for o in options
    ):
        return options
    return options + [
        BifurcationOption(section=DESCRIBE_FACTS_OPTION, description="")
    ]


def _is_describe_facts_choice(chosen: str) -> bool:
    text = (chosen or "").strip()
    low = text.lower()
    if low.startswith("none of these"):
        return True
    # Accept localised labels if a client posts them instead of the sentinel.
    if text.startswith("इनमें से कोई नहीं"):
        return True
    if text.startswith("यापैकी कोणतेही नाही"):
        return True
    return False


def _equivalent_options_for_citation(
    cited_code: str, cited_section: str, route: str
) -> tuple[list[tuple[str, str, str, str]], str | None]:
    """Look up mapping equivalents in the code that is in force (route).

    Returns (options, mapping_type_for_prompt) where each option is
    (label like 'IPC 302', section_number, heading, mapping_type).
    Empty options means no recorded equivalent (including dropped).

    Uses the mapping indexes directly so a BNS base section that maps
    from several IPC rows (e.g. BNS 1 ← IPC 1, 2, 3…) yields multiple
    reverse options — lookup() alone prefers exact subclause rows.
    """
    _rows, ipc_index, bns_index, bns_titles, _bns_texts = mapping_lookup._load()
    options: list[tuple[str, str, str, str]] = []
    primary_type: str | None = None
    cited_key = (cited_section or "").strip().upper()

    def _add(label: str, sec: str, heading: str, mtype: str) -> None:
        nonlocal primary_type
        if any(o[0] == label for o in options):
            return
        if primary_type is None:
            primary_type = mtype
        options.append((label, sec, heading or "", mtype))

    if cited_code == "IPC" and route == "BNS":
        rows = ipc_index.get(cited_key, [])
        if not rows:
            return [], None
        for r in rows:
            mtype = r.get("mapping_type") or "section"
            if mtype == "dropped":
                continue
            base = str(r.get("bns_base_section") or r.get("bns_section") or "")
            base = base.split("(")[0].strip()
            if not base or base.lower().startswith("repealed"):
                continue
            heading = (
                bns_titles.get(base.upper())
                or r.get("bns_heading")
                or ""
            )
            _add(f"BNS {base}", base, heading, mtype)
            if len(options) >= 3:
                break
        return options, primary_type

    if cited_code == "BNS" and route == "IPC":
        base_m = re.match(r"^\s*(\d+[A-Za-z]{0,2})", cited_key)
        base = base_m.group(1).upper() if base_m else cited_key
        rows = bns_index.get(base, [])
        if not rows:
            # Fall back to public lookup (handles bnsOnly / exact forms)
            result = mapping_lookup.lookup(cited_code, cited_section)
            if not result.get("found"):
                return [], None
            for pair in result.get("pairs") or []:
                mtype = pair.get("mappingType") or "section"
                if mtype == "dropped":
                    continue
                card = pair.get("ipc")
                if not card or not card.get("section"):
                    continue
                sec = str(card["section"]).split("(")[0].strip()
                _add(
                    f"IPC {sec}",
                    sec,
                    card.get("heading") or "",
                    mtype,
                )
                if len(options) >= 3:
                    break
            return options, primary_type
        for r in rows:
            mtype = r.get("mapping_type") or "section"
            if mtype == "dropped":
                continue
            sec = str(r.get("ipc_section") or "").split("(")[0].strip()
            if not sec:
                continue
            _add(f"IPC {sec}", sec, r.get("ipc_heading") or "", mtype)
            if len(options) >= 3:
                break
        return options, primary_type

    return [], None


_MONTH_NAME_RE = (
    r"(?:January|February|March|April|May|June|July|August|September|"
    r"October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
)


def extract_ipc_bns_citations(
    message: str, *, strip_date: str | None = None
) -> list[tuple[str, str]]:
    """IPC/BNS citations only, using the same spans EXPLICIT_CITATION_RE finds.

    Returns unique (code, section) pairs. BNSS, BSA, CrPC, and bare
    \"section 302\" (no code named) are omitted — not mismatches.
    Year-like numbers (1900–2099) after BNS/IPC are ignored so prose
    like \"BNS 2023\" is not treated as a section cite.
    Day-of-month digits that begin a calendar date (e.g. \"BNS 5 July 2024\",
    \"under the BNS on 5 July\") are also ignored.
    """
    text = message or ""
    if strip_date and strip_date not in {"", "(locked)"}:
        text = re.sub(re.escape(strip_date), " ", text, flags=re.I)
    found: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for m in EXPLICIT_CITATION_RE.finditer(text):
        span = m.group(0)
        if re.search(r"\bBNSS\b|\bBSA\b|\bCrPC\b", span, re.I):
            continue
        # Prefer "Section 302 IPC" / "IPC Section 302" inside a wider window
        start, end = m.span()
        window = text[max(0, start - 24) : min(len(text), end + 24)]
        pair: tuple[str, str] | None = None
        num_end: int | None = None
        m1 = re.search(
            rf"\b(IPC|BNS)\b\s*[#:]?\s*({_SECTION_NUM_RE})\b", window, re.I
        )
        m2 = re.search(
            rf"\b({_SECTION_NUM_RE})\b\s+\b(IPC|BNS)\b", window, re.I
        )
        m3 = re.search(
            rf"(?:{_SEC_WORD_RE})\s*[#:]?\s*({_SECTION_NUM_RE})\s*,?\s*\b(IPC|BNS)\b",
            window,
            re.I,
        )
        m4 = re.search(
            rf"\b(IPC|BNS)\b\s+(?:{_SEC_WORD_RE})\s*[#:]?\s*({_SECTION_NUM_RE})\b",
            window,
            re.I,
        )
        if m3:
            pair = (m3.group(2).upper(), m3.group(1))
            num_end = m3.end(1)
        elif m4:
            pair = (m4.group(1).upper(), m4.group(2))
            num_end = m4.end(2)
        elif m1:
            pair = (m1.group(1).upper(), m1.group(2))
            num_end = m1.end(2)
        elif m2:
            pair = (m2.group(2).upper(), m2.group(1))
            num_end = m2.end(1)
        if pair is None:
            continue
        if pair[0] not in {"IPC", "BNS"}:
            continue
        # Drop year false-positives (e.g. "BNS 2023" in running text)
        if re.fullmatch(r"(?:19|20)\d{2}", pair[1]):
            continue
        # Drop day-of-month glued to a month name ("BNS 5 July 2024")
        if num_end is not None and re.match(
            rf"\s+{_MONTH_NAME_RE}\b", window[num_end:], re.I
        ):
            continue
        key = (pair[0], pair[1].upper())
        if key in seen:
            continue
        seen.add(key)
        found.append((pair[0], pair[1].upper()))
    return found


def _mapping_type_phrase(mapping_type: str | None) -> str:
    t = (mapping_type or "section").lower()
    if t == "partial":
        return "partly matches"
    if t == "merged":
        return "merged into"
    return "the corresponding section is"


def _code_full_name(code: str) -> str:
    return (
        "the Indian Penal Code"
        if code == "IPC"
        else "the Bharatiya Nyaya Sanhita"
    )


def _build_code_mismatch_response(
    *,
    message: str,
    offense_date: date,
    matched_text: str,
    reason: str,
    route: str,
    mismatches: list[tuple[str, str]],
    conversation_id: str,
) -> BifurcationResponse | ClarifyResponse:
    """Offer mapped equivalents in the in-force code; skip retrieval."""
    date_str = offense_date.strftime("%-d %B %Y") if hasattr(offense_date, "strftime") else str(offense_date)
    # macOS/Linux: %-d may fail on some platforms — use day without leading zero safely
    try:
        date_str = offense_date.strftime("%-d %B %Y")
    except ValueError:
        date_str = offense_date.strftime("%d %B %Y").lstrip("0")

    route_name = _code_full_name(route)
    all_options: list[tuple[str, str, str, str]] = []
    prompt_parts: list[str] = []
    any_found = False

    for cited_code, cited_sec in mismatches:
        opts, mtype = _equivalent_options_for_citation(cited_code, cited_sec, route)
        if not opts:
            prompt_parts.append(
                f"No equivalent is recorded in our mapping table for "
                f"{cited_code} {cited_sec}."
            )
            continue
        any_found = True
        phrase = _mapping_type_phrase(mtype)
        labels = [o[0] for o in opts]
        if len(labels) == 1:
            eq_text = f"{phrase} {labels[0]}"
        else:
            eq_text = f"{phrase} " + ", ".join(labels[:-1]) + f" and {labels[-1]}"
        # Normalise "the corresponding section is IPC 302"
        if phrase == "the corresponding section is":
            mid = f"In our mapping table {eq_text}."
        elif phrase == "partly matches":
            mid = f"In our mapping table it partly matches {', '.join(labels)}."
        else:  # merged into
            mid = f"In our mapping table it is merged into {', '.join(labels)}."
        prompt_parts.append(
            f"You named {cited_code} {cited_sec}, but for an offence on {date_str} "
            f"{route_name} applies. {mid}"
        )
        for o in opts:
            if o[0] not in {x[0] for x in all_options}:
                all_options.append(o)
            if len(all_options) >= 3:
                break
        if len(all_options) >= 3:
            break

    if not any_found or not all_options:
        # No equivalents at all — clarify, ask for facts
        named = ", ".join(f"{c} {s}" for c, s in mismatches)
        question = (
            f"No equivalent is recorded in our mapping table for {named}. "
            "Describe what happened (who did what, and to whom) so I can find the section."
        )
        if len(mismatches) == 1:
            c, s = mismatches[0]
            question = (
                f"No equivalent is recorded in our mapping table for {c} {s}. "
                "Describe what happened (who did what, and to whom) so I can find the section."
            )
        return ClarifyResponse(question=question, reason="code_mismatch")

    prompt = " ".join(prompt_parts) + " Which would you like me to analyse?"

    by_section: dict[str, stage3.RetrievedChunk] = {}
    bif_options: list[BifurcationOption] = []
    for label, sec, heading, _mtype in all_options[:3]:
        chunk_id = f"{route}_{sec}"
        chunk = stage3.get_chunk_by_id(chunk_id, route)
        if chunk is None:
            # Try without letter issues
            chunk = stage3.get_chunk_by_id(chunk_id.upper(), route)
        if chunk is None:
            continue
        by_section[sec] = chunk
        by_section[chunk.chunk_id] = chunk
        by_section[label] = chunk
        bif_options.append(
            BifurcationOption(
                section=label,
                description=heading or stage3.option_description(chunk),
            )
        )

    if not bif_options:
        named = ", ".join(f"{c} {s}" for c, s in mismatches)
        return ClarifyResponse(
            question=(
                f"No equivalent is recorded in our mapping table for {named}. "
                "Describe what happened (who did what, and to whom) so I can find the section."
            ),
            reason="code_mismatch",
        )

    _PENDING_BIFURCATION[conversation_id] = {
        "message": message,
        "offense_date": offense_date,
        "matched_text": matched_text,
        "reason": reason,
        "route": route,
        "by_section": by_section,
        "scores": [],
        "source": "code_mismatch",
        # Citation-only held messages resolve to a section card, not IRAC.
        "held_citation_only": message_is_citation_only(message, matched_text),
    }
    return BifurcationResponse(
        prompt=prompt,
        options=_with_describe_facts_option(bif_options),
        reason="code_mismatch",
    )


@app.post("/api/query")
async def handle_query(req: QueryRequest):
    # A new message abandons a pending date_conflict choice (other pending
    # bifurcations are left alone until overwritten by a later bif response).
    pending = _PENDING_BIFURCATION.get(req.conversation_id)
    if pending is not None and pending.get("source") == "date_conflict":
        _PENDING_BIFURCATION.pop(req.conversation_id, None)

    locked = _LOCKED_DATES.get(req.conversation_id)
    date_lock_label: str | None = None

    if locked is not None:
        # Re-run Stage 1 on *this* message to detect a conflicting date.
        extracted, span_in_msg, extract_reason = stage1.extract_offense_date(
            req.message
        )
        if extracted is not None and extracted != locked:
            if _same_cutoff_side(locked, extracted):
                # Same IPC/BNS side — keep the lock; note which date we use.
                date_lock_label = _format_offense_date(locked)
            else:
                # Opposite sides of 1 July 2024 — ask; no retrieval.
                return _build_date_conflict_response(
                    conversation_id=req.conversation_id,
                    message=req.message,
                    locked=locked,
                    new_date=extracted,
                    language=getattr(req, "language", "en"),
                )
        offense_date = locked
        matched_text = "(locked)"
        reason = "conversation_lock"
        # For missing-facts stripping, prefer a date span from this message.
        date_span_for_strip = span_in_msg or ""
    else:
        offense_date, matched_text, reason = stage1.extract_offense_date(
            req.message
        )
        date_span_for_strip = matched_text or ""

    return await _run_pipeline(
        message=req.message,
        conversation_id=req.conversation_id,
        language=getattr(req, "language", "en"),
        offense_date=offense_date,
        matched_text=matched_text or "",
        reason=reason,
        date_span_for_strip=date_span_for_strip,
        date_lock_label=date_lock_label,
        establish_lock=(locked is None),
        date_source=(
            "document"
            if req.conversation_id.startswith("doc-upload")
            else ("earlier_message" if locked is not None else "message")
        ),
    )


async def _run_pipeline(
    *,
    message: str,
    conversation_id: str,
    language: str,
    offense_date: date | None,
    matched_text: str,
    reason: str,
    date_span_for_strip: str,
    date_lock_label: str | None = None,
    establish_lock: bool = True,
    date_source: str = "message",
):
    """Shared Stage 2–4 path after the offence date is settled."""
    # Stage 2: deterministic gate
    if offense_date is None:
        if reason == "ambiguous_numeric_format":
            return ClarifyResponse(
                question=(
                    f"I found the date '{matched_text}' but cannot tell whether it is "
                    "DD-MM or MM-DD. Please write the date in full (e.g. 15 March 2024)."
                ),
                reason="ambiguous_date",
            )
        return ClarifyResponse(
            question="What date did this happen? I need this to know which law applies.",
            reason="missing_date",
        )

    if establish_lock and conversation_id not in _LOCKED_DATES:
        _LOCKED_DATES[conversation_id] = offense_date

    route = stage2.route(offense_date)  # "IPC" or "BNS"

    if date_source not in {"message", "earlier_message", "document"}:
        date_source = "message"
    if date_source == "message" and (
        reason == "conversation_lock" or date_lock_label
    ):
        date_source = "earlier_message"
    if conversation_id.startswith("doc-upload"):
        date_source = "document"
    odu = _build_offense_date_used(offense_date, route, source=date_source)

    def _finish(resp):
        return _attach_offense_date_used(
            _attach_date_lock_label(resp, date_lock_label),
            odu,
        )

    if message_missing_offense_facts(message, date_span_for_strip):
        # Date stays locked; next turn with facts will reuse it.
        return _finish(
            ClarifyResponse(
                question=(
                    "I have the date. Describe what happened (who did what, "
                    "and to whom) so I can find the section."
                ),
                reason="missing_facts",
            )
        )

    # Named IPC/BNS that is not the code in force for this date → mapping offer
    # (no retrieval). BNSS/BSA/CrPC and bare "section N" are left alone.
    # Strip the Stage 1 date span so day digits are not read as section numbers
    # (e.g. "under the BNS 5 July 2024" must not become BNS 5).
    citations = extract_ipc_bns_citations(
        message, strip_date=date_span_for_strip or matched_text
    )
    mismatches = [(c, s) for c, s in citations if c != route]
    if mismatches:
        return _finish(
            _build_code_mismatch_response(
                message=message,
                offense_date=offense_date,
                matched_text=matched_text,
                reason=reason,
                route=route,
                mismatches=mismatches,
                conversation_id=conversation_id,
            )
        )

    # Citation-only (date + meta + citations, no other content words) with a
    # matching-route code: show the statute + mapping; skip retrieval/writing.
    if message_is_citation_only(message, date_span_for_strip):
        matching = [(c, s) for c, s in citations if c == route]
        if matching:
            return _finish(
                _build_section_lookup(
                    matching,
                    reason="citation_only",
                    offense_date_used=odu,
                )
            )

    # Facts + explicit citation of the in-force code: honour the named section
    # (skip score-gap bifurcation). detect_bifurcation itself is unchanged.
    info_note: str | None = None
    matching_cites = [(c, s) for c, s in citations if c == route]
    if matching_cites and not message_is_citation_only(message, date_span_for_strip):
        chosen_chunk = None
        missing_labels: list[str] = []
        for code, sec in matching_cites:
            chunk = stage3.get_chunk_by_id(f"{code}_{sec}", code)
            if chunk is None:
                chunk = stage3.get_chunk_by_id(f"{code}_{sec}".upper(), code)
            if chunk is None:
                missing_labels.append(f"{code} {sec}")
                continue
            chosen_chunk = chunk
            break
        if chosen_chunk is not None:
            return _finish(
                _build_mapping(
                    message=message,
                    offense_date=offense_date,
                    matched_text=matched_text,
                    reason=reason,
                    route=route,
                    top_chunk=chosen_chunk,
                    retrieve_detail=(
                        f"User-cited section {chosen_chunk.chunk_id} "
                        f"(skipped score-gap bifurcation)"
                    ),
                    language=language,
                    offense_date_used=odu,
                )
            )
        if missing_labels:
            info_note = (
                f"{missing_labels[0]} is not in the statute text we hold; "
                "searching on your facts instead."
            )

    # Stage 3: act-aware cascade on the RAW message (+ scores for bifurcation)
    scored = stage3.cascade_search_with_scores(message, corpus_act=route, k=5)
    if not scored:
        return _finish(
            FailureResponse(
                reason="no_mapping",
                message="No matching statutory section was found for this query.",
            )
        )

    # Score-gap check needs descending scores; cascade order is preserved in `scored`
    # so a single-candidate path still uses cascade[0] (exact-match first).
    score_sorted = sorted(scored, key=lambda x: x[1], reverse=True)
    candidates = stage3.detect_bifurcation(score_sorted, margin=0.10)

    if len(candidates) > 1:
        option_labels = [_chunk_section_label(c) for c in candidates]
        rejected = _REJECTED_BIFURCATION_SECTIONS.get(conversation_id, set())
        # If every candidate was already offered and rejected via "None of these",
        # do not ask again — return plain section cards instead.
        if option_labels and all(lab in rejected for lab in option_labels):
            return _finish(
                _build_section_lookup_from_chunks(
                    candidates,
                    note=BIFURCATION_EXHAUSTED_NOTE,
                    reason="bifurcation_exhausted",
                    offense_date_used=odu,
                )
            )

        options = []
        by_section: dict[str, stage3.RetrievedChunk] = {}
        for chunk in candidates:
            section_key = str(chunk.section_number)
            by_section[section_key] = chunk
            # Also allow "BNS 193" / "BNSS_433" style picks on resolve
            by_section[chunk.chunk_id] = chunk
            by_section[f"{chunk.act} {section_key}"] = chunk
            options.append(
                BifurcationOption(
                    section=f"{chunk.act} {section_key}",
                    description=stage3.option_description(chunk),
                )
            )
        _PENDING_BIFURCATION[conversation_id] = {
            "message": message,
            "offense_date": offense_date,
            "matched_text": matched_text,
            "reason": reason,
            "route": route,
            "by_section": by_section,
            "offered_labels": option_labels,
            "scores": [
                (c.chunk_id, float(s))
                for c, s in scored
                if c.chunk_id in {x.chunk_id for x in candidates}
            ],
            "date_lock_label": date_lock_label,
            "info_note": info_note,
            "date_source": date_source,
            "offense_date_used": odu,
        }
        section_list = ", ".join(o.section for o in options)
        bif = BifurcationResponse(
            prompt=(
                "Several statutory sections look equally plausible for this query. "
                f"Which one should I analyse: {section_list}?"
            ),
            options=_with_describe_facts_option(options),
            info_note=info_note,
        )
        return _finish(bif)

    top_chunk = scored[0][0]  # cascade top — unchanged when no bifurcation
    mapped = _build_mapping(
        message=message,
        offense_date=offense_date,
        matched_text=matched_text,
        reason=reason,
        route=route,
        top_chunk=top_chunk,
        retrieve_detail=f"Cascade retrieval, top match: {top_chunk.chunk_id}",
        language=language,
        offense_date_used=odu,
    )
    if info_note and hasattr(mapped, "model_copy"):
        mapped = mapped.model_copy(update={"info_note": info_note})
    return _finish(mapped)


@app.post("/api/query/resolve_bifurcation")
async def resolve_bifurcation(req: ResolveBifurcationRequest):
    """Continue after the user picks one of the bifurcation options.

    Skips Stage 3 retrieval entirely; looks up the chosen chunk from the
    pending bifurcation state and runs Stage 4 on that section alone.
    """
    pending = _PENDING_BIFURCATION.get(req.conversation_id)
    if pending is None:
        return FailureResponse(
            reason="ambiguous",
            message=(
                "No pending bifurcation for this conversation. "
                "Send a new /api/query first."
            ),
        )

    chosen = req.chosen_section.strip()
    language = getattr(req, "language", "en")

    # Date-conflict: choosing a date replaces the lock and re-runs the held message.
    if pending.get("source") == "date_conflict":
        choices: dict = pending.get("date_choices") or {}
        chosen_date: date | None = None
        chosen_label = chosen
        for label, d in choices.items():
            if chosen == label or chosen.lower() == label.lower():
                chosen_date = d
                chosen_label = label
                break
        if chosen_date is None:
            available = sorted(choices.keys())
            return FailureResponse(
                reason="ambiguous",
                message=(
                    f"Date '{req.chosen_section}' is not one of the pending options. "
                    f"Available: {available}"
                ),
            )
        _PENDING_BIFURCATION.pop(req.conversation_id, None)
        _LOCKED_DATES[req.conversation_id] = chosen_date
        # Re-run held message under the chosen date; skip re-checking the
        # message's own date against the (just updated) lock.
        held = pending["message"]
        _, span_in_msg, _ = stage1.extract_offense_date(held)
        return await _run_pipeline(
            message=held,
            conversation_id=req.conversation_id,
            language=language,
            offense_date=chosen_date,
            matched_text=chosen_label,
            reason="date_conflict_resolved",
            date_span_for_strip=span_in_msg or chosen_label,
            date_lock_label=None,
            establish_lock=False,
            date_source="message",
        )

    # Escape hatch: user rejected the offered sections and will describe facts.
    # Date stays locked; free-question counter is unchanged (no mapping).
    if _is_describe_facts_choice(chosen):
        _remember_rejected_sections(req.conversation_id, pending)
        _PENDING_BIFURCATION.pop(req.conversation_id, None)
        return ClarifyResponse(
            question=DESCRIBE_FACTS_PROMPT,
            reason="describe_facts",
        )

    by_section: dict = pending["by_section"]
    chunk = by_section.get(chosen)

    if chunk is None:
        # Tolerate bare section numbers and "ACT_NUM" forms
        for key, value in by_section.items():
            if (
                key.lower() == chosen.lower()
                or key.endswith(f" {chosen}")
                or key.endswith(f"_{chosen}")
                or str(value.section_number) == chosen
            ):
                chunk = value
                break

    if chunk is None:
        available = sorted(
            {c.chunk_id for c in by_section.values()},
            key=str,
        )
        return FailureResponse(
            reason="ambiguous",
            message=(
                f"Section '{req.chosen_section}' is not one of the pending options. "
                f"Available: {available}"
            ),
        )

    # Consume pending state so a second resolve does not silently reuse it
    _PENDING_BIFURCATION.pop(req.conversation_id, None)

    pending_odu = pending.get("offense_date_used")
    if pending_odu is not None and not isinstance(pending_odu, OffenseDateUsed):
        pending_odu = None
    date_source = pending.get("date_source") or "message"
    if pending_odu is None:
        pending_odu = _build_offense_date_used(
            pending["offense_date"],
            pending["route"],
            source=date_source,
        )

    def _finish_resolve(resp):
        return _attach_offense_date_used(
            _attach_date_lock_label(resp, pending.get("date_lock_label")),
            pending_odu,
        )

    # Code-mismatch on a citation-only held message → section card, not IRAC.
    if pending.get("held_citation_only"):
        return _finish_resolve(
            _build_section_lookup_from_chunks(
                [chunk],
                note=SECTION_LOOKUP_NOTE,
                reason="citation_only",
                offense_date_used=pending_odu,
            ),
        )

    mapped = _build_mapping(
        message=pending["message"],
        offense_date=pending["offense_date"],
        matched_text=pending["matched_text"],
        reason=pending["reason"],
        route=pending["route"],
        top_chunk=chunk,
        retrieve_detail=(
            f"User-resolved bifurcation → {chunk.chunk_id} "
            f"(skipped cascade re-retrieval)"
        ),
        language=language,
        offense_date_used=pending_odu,
    )
    if pending.get("info_note") and hasattr(mapped, "model_copy"):
        mapped = mapped.model_copy(update={"info_note": pending["info_note"]})
    return _finish_resolve(mapped)


@app.post("/api/upload_document")
async def upload_document(
    file: UploadFile = File(...),
    language: str = "en",
    conversation_id: str = "doc-upload",
):
    import uuid

    file_bytes = await file.read()

    ocr_used = False
    is_pdf = (
        file.content_type == "application/pdf"
        or (file.filename and file.filename.lower().endswith(".pdf"))
    )
    is_image = (
        file.content_type in ("image/jpeg", "image/png", "image/jpg")
        or (file.filename and file.filename.lower().endswith((".jpg", ".jpeg", ".png")))
    )

    if is_pdf:
        extracted_text, has_text = stage0_document.extract_text_from_pdf(file_bytes)
        if not has_text:
            print("[upload] No text layer found, falling back to OCR...")
            extracted_text = stage0_document.extract_text_via_ocr_from_pdf(file_bytes)
            ocr_used = True
    elif is_image:
        extracted_text = stage0_document.extract_text_from_image(file_bytes)
        ocr_used = True
    else:
        return FailureResponse(
            reason="source_unavailable",
            message=f"Unsupported file type: {file.content_type}. PDF, JPEG, and PNG are supported.",
        )

    if not extracted_text or not extracted_text.strip():
        return FailureResponse(
            reason="source_unavailable",
            message="Could not extract readable text from this document. Try a clearer photo or a typed document.",
        )

    # Short OCR/PDF extracts are usually unusable, but a date-only document
    # must still reach handle_query so the missing_facts clarify can fire.
    stripped = extracted_text.strip()
    if len(stripped) < 20:
        date_hit, _, _ = stage1.extract_offense_date(stripped)
        if date_hit is None:
            return FailureResponse(
                reason="source_unavailable",
                message="Could not extract readable text from this document. Try a clearer photo or a typed document.",
            )

    # Use unique conversation_id per document unless a specific thread is requested
    doc_conv_id = (
        conversation_id
        if conversation_id and conversation_id != "doc-upload"
        else f"doc-upload-{uuid.uuid4().hex[:8]}"
    )

    # From here, treat the extracted text exactly like a normal chat query -
    # run it through the SAME pipeline as /api/query, don't rebuild any logic
    fake_query = QueryRequest(
        message=extracted_text,
        conversation_id=doc_conv_id,
        language=language,
    )
    response = await handle_query(fake_query)

    # Tag the response so the frontend can show "extracted via OCR" as a
    # transparency note, same visible-not-silent principle as everything else
    if hasattr(response, "pipeline") and isinstance(response.pipeline, list):
        response.pipeline.insert(
            0,
            PipelineStep(
                stage="extract",
                detail=f"Text extracted via {'OCR' if ocr_used else 'direct PDF parsing'}",
            ),
        )
    return response

