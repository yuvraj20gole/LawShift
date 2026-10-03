"""Stage 4: constrained IRAC generation with Qwen2.5-3B-Instruct via Ollama.

Uses the gold retrieved chunk (not cascade retrieval) so this isolates
generation quality from retrieval errors. Test on 5 cases from the test split
before running at scale.

Requires:
    ollama serve
    ollama pull qwen2.5:3b-instruct
"""
import json
import sys
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b-instruct"
N_SAMPLES = 5


def generate_irac(question, retrieved_text, source_citation):
    prompt = f"""You are a legal text formatter. Using ONLY the statutory text provided below, answer the question in strict IRAC format (Issue, Rule, Application, Conclusion).

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
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1},
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
