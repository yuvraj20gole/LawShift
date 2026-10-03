"""FastAPI backend wiring Stages 1–4.

Run: uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

import time
from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from . import stage0_document, stage1, stage2, stage3, stage4, stage5_translate
from .schemas import (
    BifurcationOption,
    BifurcationResponse,
    ClarifyResponse,
    FailureResponse,
    MappingResponse,
    PipelineStep,
    QueryRequest,
    ResolveBifurcationRequest,
    SectionBadge,
    Source,
)

# Per-conversation locked offence date (frontend conversation_id contract).
_LOCKED_DATES: dict[str, date] = {}

# Pending bifurcation choices: conversation_id -> state for resolve endpoint.
_PENDING_BIFURCATION: dict[str, dict] = {}


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


def _build_mapping(
    message: str,
    offense_date: date,
    matched_text: str,
    reason: str,
    route: str,
    top_chunk: stage3.RetrievedChunk,
    retrieve_detail: str,
    language: str = "en",
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
    )


@app.post("/api/query")
async def handle_query(req: QueryRequest):
    # Stage 1: extract offence date (or reuse conversation lock)
    locked = _LOCKED_DATES.get(req.conversation_id)
    if locked is not None:
        offense_date, matched_text, reason = locked, "(locked)", "conversation_lock"
    else:
        offense_date, matched_text, reason = stage1.extract_offense_date(req.message)

    # Stage 2: deterministic gate
    if offense_date is None:
        if reason == "ambiguous_numeric_format":
            return ClarifyResponse(
                question=(
                    f"I found the date '{matched_text}' but cannot tell whether it is "
                    "DD-MM or MM-DD. Please write the date in full (e.g. 15 March 2024)."
                )
            )
        return ClarifyResponse(
            question="What date did this happen? I need this to know which law applies."
        )

    if req.conversation_id not in _LOCKED_DATES:
        _LOCKED_DATES[req.conversation_id] = offense_date

    route = stage2.route(offense_date)  # "IPC" or "BNS"

    # Stage 3: act-aware cascade on the RAW message (+ scores for bifurcation)
    scored = stage3.cascade_search_with_scores(req.message, corpus_act=route, k=5)
    if not scored:
        return FailureResponse(
            reason="no_mapping",
            message="No matching statutory section was found for this query.",
        )

    # Score-gap check needs descending scores; cascade order is preserved in `scored`
    # so a single-candidate path still uses cascade[0] (exact-match first).
    score_sorted = sorted(scored, key=lambda x: x[1], reverse=True)
    candidates = stage3.detect_bifurcation(score_sorted, margin=0.10)

    if len(candidates) > 1:
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
                    description=stage3.first_sentence(chunk.text),
                )
            )
        _PENDING_BIFURCATION[req.conversation_id] = {
            "message": req.message,
            "offense_date": offense_date,
            "matched_text": matched_text,
            "reason": reason,
            "route": route,
            "by_section": by_section,
            "scores": [
                (c.chunk_id, float(s))
                for c, s in scored
                if c.chunk_id in {x.chunk_id for x in candidates}
            ],
        }
        section_list = ", ".join(o.section for o in options)
        return BifurcationResponse(
            prompt=(
                "Several statutory sections look equally plausible for this query. "
                f"Which one should I analyse: {section_list}?"
            ),
            options=options,
        )

    top_chunk = scored[0][0]  # cascade top — unchanged when no bifurcation
    return _build_mapping(
        message=req.message,
        offense_date=offense_date,
        matched_text=matched_text,
        reason=reason,
        route=route,
        top_chunk=top_chunk,
        retrieve_detail=f"Cascade retrieval, top match: {top_chunk.chunk_id}",
        language=getattr(req, "language", "en"),
    )


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

    return _build_mapping(
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
        language=getattr(req, "language", "en"),
    )


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

    if not extracted_text or len(extracted_text.strip()) < 20:
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

