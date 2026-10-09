"""Pydantic response models matching the frontend AssistantMessage union."""
from typing import Literal

from pydantic import BaseModel, Field


class SectionBadge(BaseModel):
    code: Literal["IPC", "BNS"]
    section: str
    offenceName: str


class Source(BaseModel):
    statute: str
    section: str
    text: str


class PipelineStep(BaseModel):
    stage: Literal["extract", "gate", "retrieve", "synthesize"]
    detail: str


class OffenseDateUsed(BaseModel):
    """Display-only: the date and code the answer was routed on."""

    label: str = Field(description="Human date, e.g. '25 June 2024'.")
    code: Literal["IPC", "BNS"]
    source: Literal["message", "earlier_message", "document", "confirmed"] = Field(
        default="message",
        description=(
            "Where the date came from for the parenthetical note. "
            "'earlier_message' when the conversation lock supplied it; "
            "'document' when confirmed from an extract without edit; "
            "'confirmed' when the user edited the date on attach; "
            "otherwise 'message'."
        ),
    )


class FixedConclusionParts(BaseModel):
    """Structured cite for a code-written Conclusion (localise on the client)."""

    code: str
    section: str
    heading: str


class MappingResponse(BaseModel):
    kind: Literal["mapping"] = "mapping"
    summary: str
    badge: SectionBadge
    irac: dict  # {issue, rule, application, conclusion}
    sources: list[Source]
    pipeline: list[PipelineStep]
    verification: dict  # {flagged: bool, confidence_note: str}
    engine: Literal["indictrans2", "ollama_fallback", "unavailable"] | None = Field(
        default=None,
        description=(
            "Stage 5 translation engine used for IRAC fields when language != 'en'. "
            "None when output was left in English without a translation attempt. "
            "'unavailable' when a requested language cannot be served (English IRAC kept)."
        ),
    )
    translation_note: str | None = Field(
        default=None,
        description="User-facing note when translation was skipped or used a fallback engine.",
    )
    date_lock_label: str | None = Field(
        default=None,
        description=(
            "When set, the client shows a one-line note that routing used this "
            "earlier locked offence date (same side of the cutoff as a newer date "
            "named in the message)."
        ),
    )
    info_note: str | None = Field(
        default=None,
        description=(
            "Optional one-line notice (e.g. cited section missing from corpus; "
            "searching on facts instead). Not an IRAC field."
        ),
    )
    offense_date_used: OffenseDateUsed | None = Field(
        default=None,
        description="Display-only offence date + code line for mapped answers.",
    )
    fixed_conclusion: FixedConclusionParts | None = Field(
        default=None,
        description=(
            "When set (LAWSHIFT_FIXED_CONCLUSION=1), the client renders the "
            "Conclusion from a localised template using these parts; "
            "irac.conclusion holds the English fixed sentence for EN / verifier."
        ),
    )
    translation_fallback_fields: list[str] | None = Field(
        default=None,
        description=(
            "IRAC field names kept in English because Stage 5 translation "
            "changed a number (section, date, year, or amount). Empty/None "
            "when every translated field preserved its digit multiset."
        ),
    )
    application_text: str | None = Field(
        default=None,
        description=(
            "Same string as irac.application when present. Exposed so clients "
            "can treat Application as optional without parsing irac."
        ),
    )
    application_generated: bool = Field(
        default=True,
        description=(
            "True when Application was produced by the writer model. "
            "False would mean a future code-written or omitted Application."
        ),
    )
    rule_truncated: bool = Field(
        default=False,
        description=(
            "True when irac.rule is a proper prefix of the cleaned statute "
            "text (Exception / Explanation / Provided that / Illustration "
            "cut away). False when the Rule is the full cleaned section."
        ),
    )


class ClarifyResponse(BaseModel):
    kind: Literal["clarify"] = "clarify"
    question: str
    reason: Literal[
        "missing_date",
        "ambiguous_date",
        "missing_facts",
        "code_mismatch",
        "describe_facts",
    ] | None = Field(
        default=None,
        description="Why clarify was returned. None for older clients / unspecified.",
    )
    date_lock_label: str | None = Field(
        default=None,
        description="Optional locked-date note; see MappingResponse.date_lock_label.",
    )


class FailureResponse(BaseModel):
    kind: Literal["failure"] = "failure"
    reason: Literal["no_mapping", "ambiguous", "source_unavailable"]
    message: str
    date_lock_label: str | None = Field(
        default=None,
        description="Optional locked-date note; see MappingResponse.date_lock_label.",
    )


class BifurcationOption(BaseModel):
    section: str
    description: str


class BifurcationResponse(BaseModel):
    kind: Literal["bifurcation"] = "bifurcation"
    prompt: str
    options: list[BifurcationOption]
    reason: Literal["score_gap", "code_mismatch", "date_conflict"] | None = Field(
        default=None,
        description=(
            "Optional cause. 'code_mismatch' when the user named IPC/BNS "
            "that is not the code in force on the offence date. "
            "'date_conflict' when a locked offence date and a new message date "
            "fall on opposite sides of the 1 July 2024 cutoff. None or "
            "'score_gap' for ordinary close-score bifurcation."
        ),
    )
    date_lock_label: str | None = Field(
        default=None,
        description="Optional locked-date note; see MappingResponse.date_lock_label.",
    )
    info_note: str | None = Field(
        default=None,
        description="Optional one-line notice; see MappingResponse.info_note.",
    )


class SectionLookupItem(BaseModel):
    """One cited section returned without retrieval or IRAC writing."""

    code: Literal["IPC", "BNS", "BNSS", "BSA"]
    section: str
    heading: str
    text: str
    found: bool
    mapping_line: str
    # Structured mapping fields so the client can localise the line without
    # re-parsing English prose. Optional for older clients.
    mapping_status: Literal["equivalent", "none", "missing"] | None = None
    equiv_code: Literal["IPC", "BNS"] | None = None
    equiv_section: str | None = None
    equiv_heading: str | None = None
    mapping_type: Literal["section", "partial", "merged"] | None = None


class SectionLookupResponse(BaseModel):
    """Citation-only reply: show the statute (+ mapping) and ask for facts.

    Smallest new kind so the client can render a collapsed statute panel
    without treating this as a mapped answer (quota / IRAC).
    Also used when score-gap bifurcation would only re-offer sections the
    user already rejected via \"None of these\".
    """

    kind: Literal["section_lookup"] = "section_lookup"
    note: str
    items: list[SectionLookupItem]
    reason: Literal["citation_only", "bifurcation_exhausted"] | None = Field(
        default=None,
        description=(
            "Why cards were returned. 'bifurcation_exhausted' when every "
            "offered section was previously rejected; None/'citation_only' "
            "for a bare citation lookup."
        ),
    )
    date_lock_label: str | None = Field(
        default=None,
        description="Optional locked-date note; see MappingResponse.date_lock_label.",
    )
    offense_date_used: OffenseDateUsed | None = Field(
        default=None,
        description="Display-only offence date + code line for section cards.",
    )


class QueryRequest(BaseModel):
    message: str
    conversation_id: str = Field(
        ...,
        description="Locks offence date per thread once Stage 1 resolves a date.",
    )
    language: str = Field(
        default="en",
        description="Target language code for IRAC output ('en', 'hi', 'mr').",
    )


class ResolveBifurcationRequest(BaseModel):
    conversation_id: str
    chosen_section: str
    language: str = Field(
        default="en",
        description="Target language code for IRAC output ('en', 'hi', 'mr').",
    )


class CaseAttachRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1, max_length=128)
    facts_text: str = Field(..., min_length=1, max_length=6000)
    offence_date: str = Field(
        ...,
        description="Offence date as YYYY-MM-DD (validated server-side).",
    )
    date_source: Literal["document", "edited"]
    filename: str | None = Field(default=None, max_length=200)


class CaseDetachRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1, max_length=128)


AssistantResponse = (
    MappingResponse
    | ClarifyResponse
    | FailureResponse
    | BifurcationResponse
    | SectionLookupResponse
)
