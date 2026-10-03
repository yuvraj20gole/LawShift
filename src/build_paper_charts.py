"""Build publication-ready charts from sprint results.

Outputs:
  results/paper_heatmap_method_x_question_type.png
  results/paper_progression_chart.png
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # no display needed
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

# ---------------------------------------------------------------------------
# Source definitions
# Each entry: (filename, key_path_to_hit_rate_by_question_type, display_label)
# key_path is a list; an empty list means the file itself is the dict with
# hit_rate_by_question_type at the top level.
# ---------------------------------------------------------------------------
SOURCES = [
    # --- Pre-fine-tune retrieval comparison (same n=1000 sample, off-the-shelf MiniLM)
    ("retrieval_eval.json",
     ["bm25", "hit_rate_by_question_type"],
     "BM25"),
    ("retrieval_eval.json",
     ["dense", "hit_rate_by_question_type"],
     "Dense (MiniLM)"),
    ("retrieval_eval.json",
     ["hybrid", "hit_rate_by_question_type"],
     "Hybrid RRF"),
    ("retrieval_eval.json",
     ["weighted_fusion", "hit_rate_by_question_type"],
     "Weighted Fusion"),
    ("retrieval_eval.json",
     ["cascade", "hit_rate_by_question_type"],
     "Cascade (no FT)"),
    # --- Fine-tuned bge-small, test split n=636
    ("finetuned_on_test_split.json",
     ["hit_rate_by_question_type"],
     "Cascade + FT (e3)"),
    ("final_selected_model_test_eval.json",
     ["hit_rate_by_question_type"],
     "Cascade + FT (e8, FINAL)"),
]

PREFERRED_COL_ORDER = [
    "definitional_section",
    "definitional_topic",
    "elements",
    "exceptions",
    "scenario",
    "consequence",
]

# Human-readable column labels for the chart axes
COL_LABELS = {
    "definitional_section": "Def. Section",
    "definitional_topic":   "Def. Topic",
    "elements":             "Elements",
    "exceptions":           "Exceptions",
    "scenario":             "Scenario",
    "consequence":          "Consequence",
}


def load_hit_rates():
    rows = {}
    for fname, keypath, label in SOURCES:
        fpath = RESULTS / fname
        if not fpath.exists():
            print(f"MISSING: {fpath} — skipping '{label}'")
            continue
        with fpath.open() as f:
            data = json.load(f)
        raw = data
        try:
            for k in keypath:
                raw = raw[k]
        except (KeyError, TypeError) as exc:
            top_keys = list(json.loads(fpath.read_text()).keys())
            print(f"Could not extract '{label}' from {fname} at {keypath}: {exc}")
            print(f"  Top-level keys: {top_keys}")
            continue
        rows[label] = raw
        print(f"Loaded: {label:40s}  keys={list(raw.keys())}")
    return rows


def build_heatmap(rows: dict) -> pd.DataFrame:
    df = pd.DataFrame(rows).T           # rows = methods, columns = question types
    cols = [c for c in PREFERRED_COL_ORDER if c in df.columns]
    if not cols:
        cols = sorted(df.columns)
    return df[cols].astype(float)


def save_heatmap(df: pd.DataFrame, out_path: Path) -> None:
    display_cols = [COL_LABELS.get(c, c) for c in df.columns]
    n_rows, n_cols = df.shape

    fig, ax = plt.subplots(figsize=(max(7, n_cols * 1.1), max(4, n_rows * 0.6)))
    im = ax.imshow(df.values, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(range(n_cols))
    ax.set_xticklabels(display_cols, rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(df.index, fontsize=9)

    for i in range(n_rows):
        for j in range(n_cols):
            val = df.values[i, j]
            if not np.isnan(val):
                text_color = "white" if val < 0.35 or val > 0.82 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        color=text_color, fontsize=8, fontweight="bold")

    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Hit Rate @ k=5", fontsize=9)
    ax.set_title("Retrieval Method Performance by Question Type\n(k=5; pre-FT methods: n=1000; fine-tuned: n=636 test)",
                 fontsize=10, pad=10)

    # Horizontal line after the last pre-FT row (index 4 = "Cascade (no FT)")
    pre_ft_last = next(
        (i for i, lbl in enumerate(df.index) if "no FT" in lbl), None
    )
    if pre_ft_last is not None:
        ax.axhline(pre_ft_last + 0.5, color="white", linewidth=1.5, linestyle="--")

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out_path}")


def save_progression(rows: dict, out_path: Path) -> None:
    labels = list(rows.keys())
    means = [float(np.mean(list(v.values()))) for v in rows.values()]

    # Colour: red for pre-FT, amber for intermediate FT, green for final
    def bar_color(label):
        if "FINAL" in label:
            return "#2e7d32"
        if "FT" in label:
            return "#f9a825"
        return "#c62828"

    colors = [bar_color(l) for l in labels]

    fig, ax = plt.subplots(figsize=(10, 4))
    bars = ax.bar(range(len(labels)), means, color=colors, edgecolor="white", linewidth=0.8)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Mean Hit Rate @ k=5\n(avg across question types)", fontsize=9)
    ax.set_title("Retrieval Performance Progression — BM25 to Final Fine-Tuned Model",
                 fontsize=10)
    ax.set_ylim(0, 1.0)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2,
                val + 0.015, f"{val:.3f}",
                ha="center", va="bottom", fontsize=8, fontweight="bold")

    # Vertical separator before FT methods
    first_ft = next((i for i, l in enumerate(labels) if "FT" in l), None)
    if first_ft is not None:
        ax.axvline(first_ft - 0.5, color="grey", linestyle=":", linewidth=1)
        ax.text(first_ft - 0.5, 0.01, "  fine-tuning →", fontsize=8, color="grey")

    # Legend patches
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#c62828", label="Pre-FT (off-the-shelf)"),
        Patch(facecolor="#f9a825", label="Fine-tuned (intermediate)"),
        Patch(facecolor="#2e7d32", label="Fine-tuned (selected, e8)"),
    ]
    ax.legend(handles=legend_elements, loc="upper left", fontsize=8)

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out_path}")


def main():
    print("=== Loading hit-rate data ===")
    rows = load_hit_rates()
    print(f"\nSuccessfully loaded {len(rows)} methods for heatmap:")
    for label in rows:
        print(f"  - {label}")

    if not rows:
        print("No data loaded; aborting.")
        sys.exit(1)

    df = build_heatmap(rows)
    print(f"\nFull heatmap data (rounded to 3dp):\n{df.round(3).to_string()}")

    save_heatmap(df, RESULTS / "paper_heatmap_method_x_question_type.png")
    save_progression(rows, RESULTS / "paper_progression_chart.png")

    print("\nDone.")


if __name__ == "__main__":
    main()
