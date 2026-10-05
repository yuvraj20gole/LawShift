"""Stage 4: constrained IRAC generation with Qwen2.5-3B-Instruct via Ollama.

Uses the gold retrieved chunk (not cascade retrieval) so this isolates
generation quality from retrieval errors. Test on 5 cases from the test split
before running at scale.

Requires:
    ollama serve
    ollama pull qwen2.5:3b-instruct

Prompt variants (env STAGE4_PROMPT_VERSION):
    default / unset / v1 — original prompt (production default)
    v2 — careful conclusion/application wording (experimental; not the app default)
"""
import json
import os
import sys
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b-instruct"
N_SAMPLES = 5
# No seed is passed to Ollama; temperature is low but sampling is not deterministic.
TEMPERATURE = 0.1


PROMPT_V1 = """You are a legal text formatter. Using ONLY the statutory text provided below, answer the question in strict IRAC format (Issue, Rule, Application, Conclusion).

CRITICAL RULES:
- Do NOT introduce any fact, section number, or citation not present in the text below.
- Do NOT use any legal knowledge beyond what is written here.
- If the provided text does not fully answer the question, say so explicitly rather than filling gaps from general knowledge.

Retrieved statutory text ({source_citation}):
{retrieved_text}

Question: {question}

Respond in this exact format:
Issue: [one sentence]
Rule: [quote or closely paraphrase only the relevant part of the retrieved text]
Application: [how the rule applies to the question, using only the retrieved text]
Conclusion: [one sentence]
"""

PROMPT_V2 = """You are a legal text formatter. Using ONLY the statutory text provided below, answer the question in strict IRAC format (Issue, Rule, Application, Conclusion).

CRITICAL RULES:
- Do NOT introduce any fact, section number, or citation not present in the text below or in the question.
- Do NOT use any legal knowledge beyond what is written in the statutory text below.
- If the provided text does not fully answer the question, say so explicitly rather than filling gaps from general knowledge.
- Never output placeholder text such as "[one sentence]" or bracketed instructions.

FIELD RULES:
- Rule: quote only from the section text below. Include the penalty clause where the section has one.
- Application: restate only the facts stated in the question and compare them with what the Rule requires. Where an element depends on something the question does not say (whether material is obscene, intent, knowledge, a threshold, a status), say that element is not established by the facts given. Never describe a legal test as met unless the question's facts say so.
- If the section text has an Exception, Explanation or Proviso, say that it exists and may affect the result, without inventing facts about whether it applies.
- Conclusion: one sentence saying only whether the facts described appear to fall within the section as written (for example: "On the facts described, this appears to fall within IPC 292."). Do NOT say the person is guilty, liable, should be punished, shall be punished, or committed the offence.

Retrieved statutory text ({source_citation}):
{retrieved_text}

Question: {question}

Respond in this exact format:
Issue: <one sentence>
Rule: <quote or closely paraphrase only the relevant part of the retrieved text, including any penalty clause>
Application: <compare the question's facts to the Rule; mark unstated elements as not established>
Conclusion: <one sentence on whether the facts appear to fall within the section>
"""


def prompt_version() -> str:
    """Return active prompt version: 'v1' (default) or 'v2'."""
    raw = (os.environ.get("STAGE4_PROMPT_VERSION") or "v1").strip().lower()
    if raw in {"", "default", "v1", "1"}:
        return "v1"
    if raw in {"v2", "2"}:
        return "v2"
    # Unknown values fall back to production default.
    return "v1"


def build_prompt(question, retrieved_text, source_citation, version: str | None = None) -> str:
    ver = version or prompt_version()
    template = PROMPT_V2 if ver == "v2" else PROMPT_V1
    return template.format(
        source_citation=source_citation,
        retrieved_text=retrieved_text,
        question=question,
    )


def generate_irac(question, retrieved_text, source_citation):
    prompt = build_prompt(question, retrieved_text, source_citation)
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": TEMPERATURE},
        },
        timeout=180,
    )
    response.raise_for_status()
    payload = response.json()
    if "error" in payload and "response" not in payload:
        raise RuntimeError(payload["error"])
    return payload["response"]


def check_ollama(model=None):
    needed = model or MODEL
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        r.raise_for_status()
    except requests.RequestException as exc:
        print(
            "Ollama is not reachable at http://localhost:11434.\n"
            "Start it with: ollama serve\n"
            f"Then pull the model: ollama pull {needed}",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc
    names = [m.get("name", "") for m in r.json().get("models", [])]
    if not any(n == needed or n.startswith(needed) for n in names):
        print(
            f"Model {needed} is not pulled yet. Available: {names or '(none)'}\n"
            f"Run: ollama pull {needed}",
            file=sys.stderr,
        )
        raise SystemExit(1)


def main():
    check_ollama()

    statutes = pd.read_json(ROOT / "data/clean/statutes.jsonl", lines=True)
    test_set = pd.read_json(ROOT / "data/splits/test.jsonl", lines=True).head(N_SAMPLES)
    statutes_lookup = dict(zip(statutes["chunk_id"], statutes["text"]))

    records = []
    for i, row in test_set.iterrows():
        retrieved = statutes_lookup.get(row["chunk_id"], "")
        if not retrieved:
            print(f"WARNING: chunk_id {row['chunk_id']} not in statutes.jsonl — skipping")
            continue
        print(f"\n{'=' * 80}")
        print(f"[{i + 1}/{N_SAMPLES}] {row['chunk_id']}  ({row.get('question_type', '')})")
        print(f"Question: {row['question']}")
        output = generate_irac(row["question"], retrieved, row["chunk_id"])
        print(f"\nGenerated IRAC:\n{output}")
        records.append(
            {
                "chunk_id": row["chunk_id"],
                "question_type": row.get("question_type"),
                "question": row["question"],
                "gold_answer": row.get("answer"),
                "source_citation": row["chunk_id"],
                "retrieved_text": retrieved,
                "generated_irac": output,
            }
        )

    out_path = RESULTS / "stage4_sample_irac.json"
    RESULTS.mkdir(exist_ok=True)
    with out_path.open("w") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {len(records)} samples to {out_path}")


if __name__ == "__main__":
    main()
