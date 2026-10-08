"""Import build_cascade / evaluate_cascade from src/finetune_more.py.

That module runs training at import time (no ``if __name__`` guard), so this
loader executes only the shared preamble (through ``fmt``) and returns the
helper module. Cascade logic is not copied — it is the same source file.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_FINETUNE_MORE = ROOT / "src" / "finetune_more.py"
_STEP1_MARKER = (
    "# ---------------------------------------------------------------------------\n"
    "# Step 1 — val eval for existing epochs=3 model"
)


def _ensure_matplotlib_stub() -> None:
    """Preamble imports matplotlib for later charts; eval helpers do not need it."""
    if "matplotlib" in sys.modules:
        return
    mpl = types.ModuleType("matplotlib")
    pyplot = types.ModuleType("matplotlib.pyplot")
    sys.modules["matplotlib"] = mpl
    sys.modules["matplotlib.pyplot"] = pyplot
    mpl.pyplot = pyplot  # type: ignore[attr-defined]


def load_paper_cascade_module():
    """Return a module with build_cascade, evaluate_cascade, test_df, etc."""
    text = _FINETUNE_MORE.read_text(encoding="utf-8")
    if _STEP1_MARKER not in text:
        raise RuntimeError(
            f"Could not find Step 1 marker in {_FINETUNE_MORE}; "
            "refusing to import the full training script."
        )
    preamble = text.split(_STEP1_MARKER, 1)[0]
    _ensure_matplotlib_stub()
    mod = types.ModuleType("finetune_more_helpers")
    mod.__file__ = str(_FINETUNE_MORE)
    # Relative data paths in the preamble resolve against cwd (repo root).
    exec(compile(preamble, str(_FINETUNE_MORE), "exec"), mod.__dict__)
    for name in ("build_cascade", "evaluate_cascade", "test_df", "corpus_texts"):
        if not hasattr(mod, name):
            raise RuntimeError(f"preamble of finetune_more.py missing {name!r}")
    return mod
