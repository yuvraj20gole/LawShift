"""Stage 3 — act-aware cascade retrieval.

Reuses cascade_search_act_aware and NEW_CODE_ACTS from
src/end_to_end_pipeline.py. Loads models/finetuned-bge-small-ipc-bns-e8
and both corpora once at startup.

Bifurcation detection is a post-hoc score-gap check on cascade output —
it does not change retrieval ranking.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from end_to_end_pipeline import NEW_CODE_ACTS, cascade_search_act_aware as _cascade  # noqa: E402

MODEL_PATH = ROOT / "models" / "finetuned-bge-small-ipc-bns-e8"
IPC_PATH = ROOT / "data" / "clean" / "ipc_statutes.jsonl"
BNS_PATH = ROOT / "data" / "clean" / "statutes.jsonl"


@dataclass
class RetrievedChunk:
    chunk_id: str
    section_number: str
    section_title: str
    text: str
    act: str


class _Corpus:
    def __init__(self, df: pd.DataFrame, emb, acts: set[str]):
        self.df = df.reset_index(drop=True)
        self.chunk_ids = self.df["chunk_id"].tolist()
        self.section_numbers = self.df["section_number"].astype(str).str.strip().tolist()
        self.section_titles = self.df["section_title"].astype(str).tolist()
        self.texts = self.df["text"].astype(str).tolist()
        self.acts = acts
        self.emb = emb
        self.by_id = {cid: i for i, cid in enumerate(self.chunk_ids)}

    def get(self, chunk_id: str) -> RetrievedChunk:
        i = self.by_id[chunk_id]
        return RetrievedChunk(
            chunk_id=chunk_id,
            section_number=self.section_numbers[i],
            section_title=self.section_titles[i],
            text=self.texts[i],
            act=str(chunk_id).split("_", 1)[0].upper(),
        )


_model: SentenceTransformer | None = None
_ipc: _Corpus | None = None
_bns: _Corpus | None = None


def load() -> None:
    """Load embedding model + encode both corpora. Call once at app startup."""
    global _model, _ipc, _bns
    if _model is not None:
        return

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Embedding model not found: {MODEL_PATH}")
    if not IPC_PATH.exists():
        raise FileNotFoundError(f"IPC corpus not found: {IPC_PATH}")
    if not BNS_PATH.exists():
        raise FileNotFoundError(f"BNS corpus not found: {BNS_PATH}")

    print(f"[stage3] Loading embedding model: {MODEL_PATH}")
    _model = SentenceTransformer(str(MODEL_PATH))

    ipc_raw = pd.read_json(IPC_PATH, lines=True)
    ipc_df = pd.DataFrame(
        {
            "chunk_id": ipc_raw["chunk_id"],
            "section_number": ipc_raw["ipc_section"].astype(str).str.strip(),
            "section_title": ipc_raw["ipc_heading"].astype(str),
            "text": ipc_raw["text"].astype(str),
        }
    )
    print(f"[stage3] Encoding IPC corpus ({len(ipc_df)} sections)...")
    ipc_emb = _model.encode(ipc_df["text"].tolist(), show_progress_bar=True)
    _ipc = _Corpus(ipc_df, np.asarray(ipc_emb), {"IPC"})

    bns_df = pd.read_json(BNS_PATH, lines=True)
    print(f"[stage3] Encoding BNS/BNSS/BSA corpus ({len(bns_df)} sections)...")
    bns_emb = _model.encode(bns_df["text"].tolist(), show_progress_bar=True)
    _bns = _Corpus(bns_df, np.asarray(bns_emb), NEW_CODE_ACTS)
    print("[stage3] Ready.")


def _corpus_for(corpus_act: str) -> _Corpus:
    if _model is None or _ipc is None or _bns is None:
        raise RuntimeError("stage3.load() has not been called")
    return _ipc if corpus_act == "IPC" else _bns


def cascade_search_act_aware(query: str, corpus_act: str, k: int = 5) -> list[RetrievedChunk]:
    """Act-aware cascade on the RAW query. corpus_act is 'IPC' or 'BNS'."""
    corpus = _corpus_for(corpus_act)
    ids = _cascade(
        query,
        corpus.chunk_ids,
        corpus.section_numbers,
        corpus.emb,
        _model,
        corpus.acts,
        k=k,
    )
    return [corpus.get(cid) for cid in ids]


def cascade_search_with_scores(
    query: str, corpus_act: str, k: int = 5
) -> list[tuple[RetrievedChunk, float]]:
    """Same cascade retrieval, with dense cosine scores attached.

    Returns (chunk, score) in **cascade order** (exact-match short-circuit
    first, then dense). Callers that need score-descending order for
    detect_bifurcation should sort explicitly — do not reorder here, so a
    non-bifurcating path can still take cascade[0] unchanged.
    """
    corpus = _corpus_for(corpus_act)
    chunks = cascade_search_act_aware(query, corpus_act=corpus_act, k=k)
    if not chunks:
        return []

    q_emb = _model.encode([query])
    indices = [corpus.by_id[c.chunk_id] for c in chunks]
    sims = cosine_similarity(q_emb, corpus.emb[indices])[0]
    return list(zip(chunks, (float(s) for s in sims)))


def detect_bifurcation(retrieved_with_scores, margin=0.10):
    """
    retrieved_with_scores: list of (chunk, score) tuples, sorted descending.
    Returns the list of chunks considered genuine co-candidates (length 1
    if no bifurcation, 2-4 if bifurcation detected).
    """
    if len(retrieved_with_scores) < 2:
        return [retrieved_with_scores[0][0]] if retrieved_with_scores else []

    top_score = retrieved_with_scores[0][1]
    candidates = [retrieved_with_scores[0][0]]
    for chunk, score in retrieved_with_scores[1:4]:  # check up to next 3
        if score >= top_score * (1 - margin):
            candidates.append(chunk)
        else:
            break  # scores are sorted, so once the gap is too big, stop
    return candidates


def get_chunk_by_id(chunk_id: str, corpus_act: str) -> RetrievedChunk | None:
    """Look up a chunk by id within the routed corpus."""
    corpus = _corpus_for(corpus_act)
    if chunk_id not in corpus.by_id:
        return None
    return corpus.get(chunk_id)


def first_sentence(text: str) -> str:
    """Short description: first sentence of statutory text (skip context header)."""
    cleaned = text.strip()
    # Drop leading [Context: ...] blocks common in corpus text
    if cleaned.startswith("[Context:"):
        end = cleaned.find("]")
        if end != -1:
            cleaned = cleaned[end + 1 :].strip()
    for sep in (".—", ".—", ". ", ".\n"):
        idx = cleaned.find(sep)
        if idx != -1:
            return cleaned[: idx + 1].strip()
    return cleaned[:200].strip()


__all__ = [
    "RetrievedChunk",
    "cascade_search_act_aware",
    "cascade_search_with_scores",
    "detect_bifurcation",
    "first_sentence",
    "get_chunk_by_id",
    "load",
]
