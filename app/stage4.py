"""Stage 4 — constrained IRAC generation + Rule-only verification.

Generation: Ollama qwen2.5:3b-instruct, prompt from src/stage4_generate.py.
Verification: Ollama qwen2.5:14b-instruct, v2 Rule-only prompt from
src/stage4_verify_ruleonly_14b_v2.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stage4_generate import (  # noqa: E402
    MODEL as GEN_MODEL,
    OLLAMA_URL,
    generate_irac as _generate_irac,
)
from stage4_verify import parse_irac  # noqa: E402
from stage4_verify_ruleonly import parse_ruleonly_verdict  # noqa: E402
from stage4_verify_ruleonly_14b_v2 import (  # noqa: E402
    MODEL as VERIFY_MODEL,
    verify_rule_only_14b_v2 as _verify,
)

TAGS_URL = "http://localhost:11434/api/tags"
REQUIRED_MODELS = (GEN_MODEL, VERIFY_MODEL)


def check_ollama() -> None:
    """Fail fast if Ollama is down or required models are missing."""
    try:
        r = requests.get(TAGS_URL, timeout=5)
        r.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            "Ollama is not reachable at http://localhost:11434.\n"
            "Start it with: ollama serve\n"
            f"Then pull: ollama pull {GEN_MODEL} && ollama pull {VERIFY_MODEL}"
        ) from exc

    names = [m.get("name", "") for m in r.json().get("models", [])]
    missing = [m for m in REQUIRED_MODELS if not any(n == m or n.startswith(m) for n in names)]
    if missing:
        raise RuntimeError(
            f"Ollama is up but missing models: {missing}. Available: {names or '(none)'}\n"
            + "\n".join(f"  ollama pull {m}" for m in missing)
        )


def generate_irac(question: str, retrieved_text: str, source_citation: str) -> str:
    """Exact prompt/path from src/stage4_generate.generate_irac."""
    return _generate_irac(question, retrieved_text, source_citation)


def verify_rule_only_14b_v2(rule_text: str, conclusion_text: str) -> tuple[str, str]:
    """Exact v2 Rule-only verifier from src/stage4_verify_ruleonly_14b_v2.py."""
    return _verify(rule_text, conclusion_text)


__all__ = [
    "check_ollama",
    "generate_irac",
    "parse_irac",
    "verify_rule_only_14b_v2",
    "GEN_MODEL",
    "VERIFY_MODEL",
]
