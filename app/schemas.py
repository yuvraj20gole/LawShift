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


class ClarifyResponse(BaseModel):
    kind: Literal["clarify"] = "clarify"
    question: str


class FailureResponse(BaseModel):
    kind: Literal["failure"] = "failure"
    reason: Literal["no_mapping", "ambiguous", "source_unavailable"]
    message: str


class BifurcationOption(BaseModel):
    section: str
    description: str


class BifurcationResponse(BaseModel):
    kind: Literal["bifurcation"] = "bifurcation"
    prompt: str
    options: list[BifurcationOption]


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


AssistantResponse = (
    MappingResponse | ClarifyResponse | FailureResponse | BifurcationResponse
)
