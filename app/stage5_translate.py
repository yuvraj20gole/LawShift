"""Stage 5 — Multilingual post-processing via IndicTrans2.

Translates user-facing IRAC outputs into Indic languages (e.g. Hindi, Marathi)
as a purely post-hoc step after Stage 4 synthesis and verification.
Never touches retrieval, gating, or verification.
"""
from __future__ import annotations

import os

# Preserve CPU/MPS PyTorch optimizations
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")
os.environ.setdefault("USE_TF", "0")

# IndicTrans2 remote config still imports transformers.onnx, which was removed
# in transformers>=5. Provide a minimal shim only when the real package is gone.
def _ensure_transformers_onnx_shim() -> None:
    import sys
    import types

    try:
        import transformers.onnx  # noqa: F401
        return
    except ModuleNotFoundError:
        pass

    if "transformers.onnx" in sys.modules and hasattr(
        sys.modules["transformers.onnx"], "OnnxConfig"
    ):
        return

    onnx = types.ModuleType("transformers.onnx")
    utils = types.ModuleType("transformers.onnx.utils")

    class OnnxConfig:  # noqa: D401 — stub for IndicTrans2 remote code
        """Minimal stand-in for removed transformers.onnx.OnnxConfig."""

    class OnnxConfigWithPast(OnnxConfig):
        """Minimal stand-in for removed OnnxConfigWithPast."""

    class OnnxSeq2SeqConfigWithPast(OnnxConfig):
        """Minimal stand-in for removed OnnxSeq2SeqConfigWithPast."""

    def compute_effective_axis_dimension(*_args, **_kwargs):
        return 1

    onnx.OnnxConfig = OnnxConfig
    onnx.OnnxConfigWithPast = OnnxConfigWithPast
    onnx.OnnxSeq2SeqConfigWithPast = OnnxSeq2SeqConfigWithPast
    onnx.utils = utils
    utils.compute_effective_axis_dimension = compute_effective_axis_dimension
    sys.modules["transformers.onnx"] = onnx
    sys.modules["transformers.onnx.utils"] = utils


# Clear a stale stub if a real transformers.onnx was reinstalled later.
import sys as _sys

if "transformers.onnx" in _sys.modules and not getattr(
    _sys.modules["transformers.onnx"], "__file__", None
):
    _sys.modules.pop("transformers.onnx", None)
    _sys.modules.pop("transformers.onnx.utils", None)

_ensure_transformers_onnx_shim()

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MODEL_NAME = "ai4bharat/indictrans2-en-indic-1B"
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

LANG_CODES = {
    "hi": "hin_Deva",
    "mr": "mar_Deva",
}

_tokenizer = None
_model = None
_ip = None


_INDIC_TRIED = False
_INDIC_AVAILABLE = False


def _get_indic_processor():
    """Resolve IndicProcessor without failing module import when deps are missing."""
    try:
        from IndicTransToolkit.processor import IndicProcessor
        return IndicProcessor(inference=True)
    except Exception as e:
        print(f"[stage5] IndicTransToolkit unavailable ({e}); trying local fallback…")
        try:
            from .indic_processor import IndicProcessor
            return IndicProcessor(inference=True)
        except Exception as e2:
            raise RuntimeError(
                f"No IndicProcessor available (toolkit={e}; local={e2})"
            ) from e2


def load_translator():
    """Lazy load IndicTrans2 model and processor."""
    global _tokenizer, _model, _ip, _INDIC_TRIED, _INDIC_AVAILABLE
    if _model is not None:
        return _tokenizer, _model, _ip

    if _INDIC_TRIED and not _INDIC_AVAILABLE:
        raise RuntimeError("IndicTrans2 previously failed to load or is inaccessible.")

    # Prefer IndicTrans2 when available; set LAWSHIFT_FORCE_OLLAMA_TRANSLATE=1
    # only for emergency offline debugging.
    if os.environ.get("LAWSHIFT_FORCE_OLLAMA_TRANSLATE", "0") == "1":
        _INDIC_TRIED = True
        raise RuntimeError(
            "Skipping IndicTrans2 (LAWSHIFT_FORCE_OLLAMA_TRANSLATE=1); using Ollama fallback."
        )

    # Prefer explicit env token; otherwise reuse the cached Hugging Face login.
    if not os.environ.get("HUGGINGFACE_HUB_TOKEN") and not os.environ.get("HF_TOKEN"):
        try:
            from huggingface_hub import get_token

            cached = get_token()
            if cached:
                os.environ["HUGGINGFACE_HUB_TOKEN"] = cached
                os.environ.setdefault("HF_TOKEN", cached)
        except Exception as exc:
            print(f"[stage5] Could not read cached HF token: {exc}")

    _INDIC_TRIED = True
    print(f"[stage5] Loading IndicTrans2 ({MODEL_NAME}) on {DEVICE}...")
    _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    _model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_NAME, trust_remote_code=True
    ).to(DEVICE)
    _model.eval()
    _ip = _get_indic_processor()
    _INDIC_AVAILABLE = True
    print("[stage5] IndicTrans2 loaded successfully.")
    return _tokenizer, _model, _ip


import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b-instruct"
# Keep fallback responsive; long hangs block the single-worker API.
OLLAMA_TIMEOUT = 90


def _translate_ollama(text: str, target_lang: str) -> str:
    """Fallback translator using local Qwen when IndicTrans2 is unavailable."""
    lang_name = "Hindi" if target_lang == "hi" else "Marathi" if target_lang == "mr" else target_lang
    prompt = f"""You are a professional legal translator specializing in Indian legal terminology.
Translate the following legal text accurately into formal, fluent {lang_name} (in Devanagari script).
Preserve all section numbers, act names, and legal meanings exactly.
Output ONLY the direct translation and nothing else.

English text:
{text}"""

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "keep_alive": "30m",
                "options": {"temperature": 0.0},
            },
            timeout=OLLAMA_TIMEOUT,
        )
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as exc:
        print(f"[stage5] Ollama fallback translation error: {exc}")
        return text


def _translate_irac_ollama(irac: dict, target_lang: str) -> dict:
    """Translate all IRAC string fields in a single Ollama call (faster than 4 round-trips)."""
    lang_name = "Hindi" if target_lang == "hi" else "Marathi" if target_lang == "mr" else target_lang
    fields = {k: v for k, v in irac.items() if isinstance(v, str) and v.strip()}
    if not fields:
        return irac

    numbered = "\n\n".join(f"[{key}]\n{text}" for key, text in fields.items())
    prompt = f"""You are a professional legal translator specializing in Indian legal terminology.
Translate each labelled block into formal, fluent {lang_name} (Devanagari script).
Preserve section numbers, act names, and legal meaning.
Return ONLY the same labelled blocks with translated text — no commentary.

{numbered}"""

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "keep_alive": "30m",
                "options": {"temperature": 0.0},
            },
            timeout=OLLAMA_TIMEOUT,
        )
        r.raise_for_status()
        raw = r.json().get("response", "").strip()
    except Exception as exc:
        print(f"[stage5] Batched Ollama IRAC translation error: {exc}")
        return {
            k: _translate_ollama(v, target_lang) if isinstance(v, str) else v
            for k, v in irac.items()
        }

    out = dict(irac)
    for key in fields:
        marker = f"[{key}]"
        if marker not in raw:
            out[key] = _translate_ollama(fields[key], target_lang)
            continue
        after = raw.split(marker, 1)[1]
        # Stop at the next labelled block if present
        next_idx = len(after)
        for other in fields:
            if other == key:
                continue
            needle = f"[{other}]"
            pos = after.find(needle)
            if pos != -1:
                next_idx = min(next_idx, pos)
        out[key] = after[:next_idx].strip() or fields[key]
    return out


def translate_text(text: str, target_lang: str) -> str:
    """Translate a single string from English to target_lang ('hi', 'mr')."""
    if not text or not text.strip():
        return text
    if target_lang == "en":
        return text
    return _translate_indic_batch([text], target_lang)[0]


def _translate_indic_batch(texts: list[str], target_lang: str) -> list[str]:
    """Run IndicTrans2 once over a list of English strings (batched generate)."""
    tgt_code = LANG_CODES.get(target_lang)
    if not tgt_code:
        raise ValueError(
            f"Unsupported target language: '{target_lang}'. Supported: {list(LANG_CODES.keys())}"
        )

    tokenizer, model, ip = load_translator()

    # Preserve empty strings without wasting generate slots.
    nonempty_idx = [i for i, t in enumerate(texts) if isinstance(t, str) and t.strip()]
    if not nonempty_idx:
        return list(texts)

    nonempty = [texts[i] for i in nonempty_idx]
    batch = ip.preprocess_batch(nonempty, src_lang="eng_Latn", tgt_lang=tgt_code)
    inputs = tokenizer(
        batch,
        truncation=True,
        padding="longest",
        return_tensors="pt",
    ).to(DEVICE)

    with torch.no_grad():
        generated = model.generate(
            **inputs,
            use_cache=True,
            min_length=0,
            # Cap new tokens (not total length) so short fields don't pad to 512.
            max_new_tokens=256,
            num_beams=5,
            num_return_sequences=1,
        )

    if DEVICE == "mps":
        torch.mps.synchronize()

    decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
    translated = ip.postprocess_batch(decoded, lang=tgt_code)

    out = list(texts)
    for i, tr in zip(nonempty_idx, translated):
        out[i] = tr
    return out


def translate_irac(irac: dict, target_lang: str) -> tuple[dict, str | None, str | None]:
    """Translate all four IRAC fields.

    Returns (irac_dict, engine, note) where engine is "indictrans2",
    "ollama_fallback", "unavailable", or None when no translation was attempted.
    """
    if target_lang == "en" or not target_lang:
        return irac, None, None

    try:
        load_translator()
    except Exception as exc:
        # Do not use Ollama for hi/mr — it has altered dates/subjects.
        if target_lang in {"hi", "mr"}:
            lang_name = "Hindi" if target_lang == "hi" else "Marathi"
            note = (
                f"{lang_name} translation is not currently available. Showing English."
            )
            print(
                f"[stage5] IndicTrans2 unavailable ({type(exc).__name__}: {exc}); {note}"
            )
            return irac, "unavailable", note
        print(
            f"[stage5] IndicTrans2 unavailable ({type(exc).__name__}: {exc}); "
            f"using batched Ollama fallback for '{target_lang}'"
        )
        return (
            _translate_irac_ollama(irac, target_lang),
            "ollama_fallback",
            "Machine-translated with a fallback model. Verify against the English text.",
        )

    import time

    keys = list(irac.keys())
    values = [irac[k] if isinstance(irac[k], str) else "" for k in keys]
    t0 = time.perf_counter()
    try:
        translated_vals = _translate_indic_batch(values, target_lang)
    except Exception as exc:
        # Batch path failed after load — do not silently Ollama-corrupt hi/mr.
        if target_lang in {"hi", "mr"}:
            lang_name = "Hindi" if target_lang == "hi" else "Marathi"
            note = (
                f"{lang_name} translation is not currently available. Showing English."
            )
            print(f"[stage5] IndicTrans2 batch failed ({exc}); {note}")
            return irac, "unavailable", note
        raise
    dt = time.perf_counter() - t0
    print(
        f"[stage5] IndicTrans2 batched {len(keys)} fields → '{target_lang}' in {dt:.2f}s"
    )

    translated = {
        k: (translated_vals[i] if isinstance(irac[k], str) else irac[k])
        for i, k in enumerate(keys)
    }
    return translated, "indictrans2", None


__all__ = ["translate_text", "translate_irac", "load_translator", "LANG_CODES"]
