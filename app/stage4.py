"""Stage 4 — Issue/Application generation + Rule-only verification.

Generation: Ollama qwen2.5:3b-instruct. The app prompt asks only for Issue and
Application; Rule and Conclusion are filled in by code in app/main.py.
Verification: Ollama qwen2.5:14b-instruct, v2 Rule-only prompt from
src/stage4_verify_ruleonly_14b_v2.py. Optional Application-aware check behind
LAWSHIFT_VERIFY_WITH_APPLICATION (default off).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from stage4_generate import (  # noqa: E402
    MODEL as GEN_MODEL,
    OLLAMA_URL,
    TEMPERATURE,
)
from stage4_verify import parse_irac  # noqa: E402
from stage4_verify_ruleonly import parse_ruleonly_verdict  # noqa: E402
from stage4_verify_ruleonly_14b_v2 import (  # noqa: E402
    FEW_SHOT_EXAMPLES,
    MODEL as VERIFY_MODEL,
    verify_rule_only_14b_v2 as _verify_rule_conclusion,
)

TAGS_URL = "http://localhost:11434/api/tags"
REQUIRED_MODELS = (GEN_MODEL, VERIFY_MODEL)

# Writer produces Issue + Application only; Rule/Conclusion are code-filled.
PROMPT_ISSUE_APPLICATION = """You are a legal text formatter. Using ONLY the statutory text provided below and the facts in the question, write Issue and Application only.

CRITICAL RULES:
- Do NOT introduce any fact, section number, or citation not present in the text below or in the question.
- Do NOT use any legal knowledge beyond what is written in the statutory text below.
- Do NOT write a Rule or Conclusion section.
- If the provided text does not fully answer the question, say so explicitly rather than filling gaps from general knowledge.
- Never output placeholder text such as "[one sentence]" or bracketed instructions.

FIELD RULES:
- Issue: one sentence stating the legal question raised by the facts.
- Application: restate only the facts stated in the question and compare them with what the statutory text requires. Where an element depends on something the question does not say, say that element is not established by the facts given. Never describe a legal test as met unless the question's facts say so.
- If the section text has an Exception, Explanation or Proviso, say that it exists and may affect the result, without inventing facts about whether it applies.

Retrieved statutory text ({source_citation}):
{retrieved_text}

Question: {question}

Respond in this exact format:
Issue: <one sentence>
Application: <compare the question's facts to the statutory text; mark unstated elements as not established>
"""


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


def verify_with_application_enabled() -> bool:
    """LAWSHIFT_VERIFY_WITH_APPLICATION: default off. Set 1 to include Application."""
    raw = os.environ.get("LAWSHIFT_VERIFY_WITH_APPLICATION", "0").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def generate_irac(question: str, retrieved_text: str, source_citation: str) -> str:
    """Generate Issue + Application only (same entrypoint name as before for stubs)."""
    prompt = PROMPT_ISSUE_APPLICATION.format(
        source_citation=source_citation,
        retrieved_text=retrieved_text,
        question=question,
    )
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": GEN_MODEL,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "30m",
            "options": {"temperature": TEMPERATURE},
        },
        timeout=180,
    )
    response.raise_for_status()
    payload = response.json()
    if "error" in payload and "response" not in payload:
        raise RuntimeError(payload["error"])
    return payload["response"]


def verify_rule_only_14b_v2(
    rule_text: str,
    conclusion_text: str,
    application_text: str | None = None,
) -> tuple[str, str]:
    """Rule+Conclusion verifier; optionally also sees Application when passed."""
    if application_text is not None:
        return verify_rule_conclusion_application(
            rule_text, application_text, conclusion_text
        )
    return _verify_rule_conclusion(rule_text, conclusion_text)


def verify_rule_conclusion_application(
    rule_text: str,
    application_text: str,
    conclusion_text: str,
    model: str = VERIFY_MODEL,
    timeout: int = 600,
) -> tuple[str, str]:
    """Same SUPPORTED/NOT_SUPPORTED contract, with Application in the prompt."""
    prompt = f"""You are a strict legal fact-checker. You will be given a statutory
Rule, an Application of that Rule to facts, and a Conclusion someone reached.
Do NOT assume the Conclusion's reasoning is correct. Independently determine
whether the Rule and Application, read together, actually support the Conclusion.

IMPORTANT CRITERIA:
- Only judge NOT_SUPPORTED if the Conclusion states something the Rule
  text does NOT address at all, or something the Rule text actively
  contradicts, or something the Application invents that the Rule does not
  support.
- Do NOT judge NOT_SUPPORTED merely because the Conclusion is a shortened,
  paraphrased, or partial restatement of the Rule - compression and
  summarization are expected and acceptable.
- Do NOT flag NOT_SUPPORTED because the Conclusion mentions a section
  number, act name, or citation label that does not literally appear in
  the Rule text. The Rule snippet is often provided without its own
  section header. Judge only the SUBSTANTIVE legal claim in the
  Conclusion - who is liable, under what conditions, and what the
  consequence is - against what the Rule text establishes. Citation
  labels are not something this check should evaluate.
- Focus specifically on: does the Conclusion's core claim (yes/no,
  who/what/when) match what the Rule actually establishes, given the
  Application's comparison of facts to the Rule?

{FEW_SHOT_EXAMPLES}

Now judge this case:

Rule: {rule_text}

Application: {application_text}

Conclusion someone reached: {conclusion_text}

Answer with exactly one word first - either SUPPORTED or NOT_SUPPORTED -
followed by one sentence of explanation."""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "30m",
            "options": {"temperature": 0.0},
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    if "error" in payload and "response" not in payload:
        raise RuntimeError(payload["error"])
    text = payload["response"].strip()
    return parse_ruleonly_verdict(text), text


__all__ = [
    "check_ollama",
    "generate_irac",
    "parse_irac",
    "verify_rule_only_14b_v2",
    "verify_rule_conclusion_application",
    "verify_with_application_enabled",
    "GEN_MODEL",
    "VERIFY_MODEL",
]
