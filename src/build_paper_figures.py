"""Generate Results-section figures and tables for the paper.

Pulls metrics from results/*.json. Saves high-resolution PNGs to paper_figures/.
Figure 2/3 (heatmap + progression) are reused from results/ if present.

Run: python3 src/build_paper_figures.py
"""
import json
import shutil
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = ROOT / "paper_figures"
DPI = 300  # print-ready


def pct(x, digits=1):
    return f"{x * 100:.{digits}f}%"


def load_json(name):
    return json.load(open(RESULTS / name))


def save_table_png(rows, columns, path, figsize=(7.0, 2.0), col_widths=None):
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")
    tbl = ax.table(
        cellText=rows,
        colLabels=columns,
        cellLoc="left",
        loc="center",
        colWidths=col_widths,
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(7.5)
    tbl.scale(1, 1.55)
    for (r, c), cell in tbl.get_celld().items():
        if r == 0:
            cell.set_text_props(weight="bold")
            cell.set_facecolor("#e8e8e8")
    plt.tight_layout()
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def table4_stage1():
    real = load_json("stage1_real_eval.json")
    stress = load_json("stage1_v2_eval.json")
    n_real = real["n"]
    n_stress = len(stress["stress_results"])
    real_acc = real["routing_accuracy"]
    stress_score = stress["stress_test_score"]
    combined = f"{n_real + int(stress_score.split('/')[0])}/{n_real + int(stress_score.split('/')[1])}"

    rows = [
        ["Real GovIntel temporal cases", str(n_real), pct(real_acc), pct(real["date_exact_match_accuracy"])],
        ["Adversarial stress test (v2)", stress_score.split("/")[1], stress_score, "—"],
        ["Combined", combined.split("/")[1], combined, "—"],
    ]
    cols = ["Evaluation set", "n", "Routing accuracy", "Date extraction"]
    print("\n=== Table 4: Stage 1 Validation ===")
    print(pd.DataFrame(rows, columns=cols).to_string(index=False))
    print(f"Sources: stage1_real_eval.json, stage1_v2_eval.json")
    save_table_png(
        rows,
        cols,
        OUT / "table4_stage1_validation.png",
        figsize=(7.0, 1.6),
        col_widths=[0.38, 0.08, 0.22, 0.22],
    )
    print(f"Saved {OUT / 'table4_stage1_validation.png'}")


def confirm_figures_2_3():
    print("\n=== Figures 2 & 3 (reuse existing) ===")
    mapping = {
        "paper_heatmap_method_x_question_type.png": "figure2_retrieval_heatmap.png",
        "paper_progression_chart.png": "figure3_retrieval_progression.png",
    }
    for src_name, dst_name in mapping.items():
        src = RESULTS / src_name
        dst = OUT / dst_name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"{src_name}: EXISTS — copied to paper_figures/{dst_name}")
        else:
            print(f"{src_name}: MISSING — run src/build_paper_charts.py first")


def table5_failed_improvements():
    xref = load_json("cross_reference_step1_2_eval.json")
    step3 = load_json("step3_cross_encoder_eval.json")
    step4 = load_json("step4_val_comparison.json")
    combined = load_json("combined_val_comparison.json")

    before_r = xref["original_corpus"]["strict_recall_at_5"]
    after_r_xref = xref["augmented_corpus"]["strict_recall_at_5"]
    before_r3 = step3["baseline"]["recall_at_k"]
    after_r3 = step3["reranked"]["recall_at_k"]
    before_ndcg = step4["original-e8"]["ndcg_at_k"]
    after_hn = step4["hardneg-e8"]["ndcg_at_k"]
    after_comb = combined["combined-e5"]["ndcg_at_k"]

    rows = [
        [
            "Cross-reference augmentation",
            f"{before_r:.3f}",
            f"{after_r_xref:.3f}",
            "Diluted embedding specificity",
            "cross_reference_step1_2_eval.json",
        ],
        [
            "Cross-encoder re-ranking",
            f"{before_r3:.3f}",
            f"{after_r3:.3f}",
            "Hurt narrative-style (scenario) queries",
            "step3_cross_encoder_eval.json",
        ],
        [
            "Hard-negative mining",
            f"{before_ndcg:.3f}",
            f"{after_hn:.3f}",
            "Likely false-negative contamination",
            "step4_val_comparison.json",
        ],
        [
            "Combined GovIntel training",
            f"{before_ndcg:.3f}",
            f"{after_comb:.3f}",
            "Distribution shift vs. validation set",
            "combined_val_comparison.json",
        ],
    ]
    cols = ["Method", "Before", "After", "Cause", "Source file"]
    print("\n=== Table 5: Attempted Improvements (Recall@5 or NDCG@5 on val, n=635) ===")
    print(pd.DataFrame(rows, columns=cols).to_string(index=False))
    save_table_png(
        [[r[0], r[1], r[2], r[3]] for r in rows],
        cols[:4],
        OUT / "table5_failed_improvements.png",
        figsize=(7.0, 2.0),
        col_widths=[0.30, 0.10, 0.10, 0.50],
    )
    print(f"Saved {OUT / 'table5_failed_improvements.png'}")


def table6_specialization():
    unified = load_json("final_unified_model_comparison.json")
    e8 = unified["e8"]["by_source"]
    c5 = unified["combined_e5"]["by_source"]

    rows = [
        ["GSMS-B val (n=635)", pct(e8["GSMS-B_val"]), pct(c5["GSMS-B_val"])],
        ["GovIntel clean (n=309)", pct(e8["GovIntel_clean"]), pct(c5["GovIntel_clean"])],
        ["  ↳ GovIntel IPC (n=302)", pct(unified["e8"]["by_source_route"]["GovIntel_clean|IPC"]["recall_at_5"]),
         pct(unified["combined_e5"]["by_source_route"]["GovIntel_clean|IPC"]["recall_at_5"])],
        ["Overall unified (n=944)", pct(unified["e8"]["overall"]), pct(unified["combined_e5"]["overall"])],
    ]
    cols = ["Source", "Primary (e8)", "Combined (e5)"]
    print("\n=== Table 6: Model Specialization (Recall@5) ===")
    print(json.dumps(unified, indent=2))
    print()
    print(pd.DataFrame(rows, columns=cols).to_string(index=False))
    save_table_png(
        rows,
        cols,
        OUT / "table6_specialization.png",
        figsize=(6.5, 1.8),
        col_widths=[0.45, 0.27, 0.28],
    )
    print(f"Saved {OUT / 'table6_specialization.png'}")


def verifier_row(label, path, recall_key="recall", prec_key="precision"):
    d = load_json(path)
    if "model_14b" in path and path == "stage4_verifier_ablation.json":
        d = d["model_14b"]
    tp, fp = d["tp"], d["fp"]
    fn, tn = d["fn"], d["tn"]
    n_pos = tp + fn
    n_flagged = tp + fp
    recall = d.get(recall_key, tp / n_pos if n_pos else 0)
    precision = d.get(prec_key, tp / n_flagged if n_flagged else 0)
    return [label, pct(recall), pct(precision), f"{tp}/5", str(fp), path]


def table7_verifiers():
    configs = [
        ("3B, Rule+App+Conc", "stage4_verifier_eval.json"),
        ("14B, Rule+App+Conc", "stage4_verifier_ablation.json"),  # model_14b handled below
        ("3B, Rule-only (v1)", "stage4_verifier_ruleonly.json"),
        ("14B, Rule-only (v1)", "stage4_verifier_ruleonly_14b.json"),
        ("Claude, Rule-only (v1)", "stage4_verifier_claude.json"),
        ("14B, Rule-only (v2)", "stage4_verifier_14b_v2.json"),
        ("Claude, Rule-only (v2)", "stage4_verifier_claude_v2.json"),
    ]
    rows = []
    print("\n=== Table 7: Verifier Configurations (40 gold-chunk cases) ===")
    for label, fname in configs:
        if fname == "stage4_verifier_ablation.json":
            d = load_json(fname)["model_14b"]
            tp, fp, fn = d["tp"], d["fp"], d["fn"]
            recall = d["recall"]
            precision = d["precision"]
        else:
            d = load_json(fname)
            tp, fp, fn = d["tp"], d["fp"], d["fn"]
            recall = tp / 5
            precision = tp / (tp + fp) if (tp + fp) else 0
        row = [label, pct(recall), pct(precision), f"{tp}/5", str(fp), fname]
        rows.append(row)
        print(f"  {label}: TP={tp}/5 FP={fp}  P={precision:.3f}  R={recall:.3f}  ({fname})")

    cols = ["Configuration", "Recall", "Precision", "TP", "FP"]
    print()
    print(pd.DataFrame([r[:5] for r in rows], columns=cols).to_string(index=False))
    save_table_png(
        [r[:3] for r in rows],
        cols[:3],
        OUT / "table7_verifier_configs.png",
        figsize=(6.5, 2.6),
        col_widths=[0.42, 0.18, 0.22],
    )
    print(f"Saved {OUT / 'table7_verifier_configs.png'}")


def figure4_irac_panel():
    cases = {c["case_number"]: c for c in load_json("stage4_larger_sample.json")}
    clean = cases[2]   # BSA_160 — grounded & consistent
    flagged = cases[39]  # BNSS_193 — Rule/Conclusion mismatch

    def wrap_block(title, case, badge, color):
        irac = case["generated_irac"].strip()
        q = case["question"].strip()
        body = textwrap.fill(q, width=88)
        irac_wrapped = "\n".join(textwrap.fill(line, width=88) if line.strip() else "" for line in irac.splitlines())
        return (
            f"{badge}  {title}\n"
            f"Case {case['case_number']} · {case['chunk_id']} · {case['question_type']}\n"
            f"{'─' * 90}\n"
            f"Question: {body}\n\n"
            f"{irac_wrapped}\n"
        )

    text_clean = wrap_block("Clean (grounded & consistent)", clean, "✓", "#2e7d32")
    text_flagged = wrap_block("Flagged (Rule/Conclusion mismatch)", flagged, "⚠", "#c62828")

    fig, axes = plt.subplots(2, 1, figsize=(7.0, 8.5))
    for ax, txt, bg in zip(
        axes,
        [text_clean, text_flagged],
        ["#f1f8f4", "#fdf3f3"],
    ):
        ax.axis("off")
        ax.text(
            0.02,
            0.98,
            txt,
            transform=ax.transAxes,
            fontsize=6.5,
            verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.4", facecolor=bg, edgecolor="#cccccc"),
        )
    fig.suptitle("Figure 4: Stage 4 IRAC Generation — Clean vs. Flagged Example", fontsize=9, y=0.995)
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    path = OUT / "figure4_stage4_irac_examples.png"
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print("\n=== Figure 4 source cases ===")
    print(f"Clean: case {clean['case_number']} ({clean['chunk_id']})")
    print(f"  Q: {clean['question'][:100]}...")
    print(f"Flagged: case {flagged['case_number']} ({flagged['chunk_id']})")
    print(f"  Q: {flagged['question'][:100]}...")
    print(f"Saved {path}")


def figure_verifier_precision_recall():
    """Supplementary: precision-recall for Rule-only configs."""
    entries = [
        ("3B v1", "stage4_verifier_ruleonly.json"),
        ("14B v1", "stage4_verifier_ruleonly_14b.json"),
        ("Claude v1", "stage4_verifier_claude.json"),
        ("14B v2", "stage4_verifier_14b_v2.json"),
        ("Claude v2", "stage4_verifier_claude_v2.json"),
    ]
    labels, precs, recs = [], [], []
    for label, fname in entries:
        d = load_json(fname)
        tp, fp = d["tp"], d["fp"]
        labels.append(label)
        precs.append(tp / (tp + fp) if (tp + fp) else 0)
        recs.append(tp / 5)

    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    x = np.arange(len(labels))
    w = 0.35
    ax.bar(x - w / 2, recs, w, label="Recall", color="#1565c0")
    ax.bar(x + w / 2, precs, w, label="Precision", color="#ef6c00")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("Rule-only Verifier: Precision vs. Recall (40 cases)")
    ax.legend(fontsize=8)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    path = OUT / "figure5_verifier_ruleonly_comparison.png"
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"\nSaved supplementary {path}")


def main():
    OUT.mkdir(exist_ok=True)
    print("Generating paper figures/tables → paper_figures/")
    table4_stage1()
    confirm_figures_2_3()
    table5_failed_improvements()
    table6_specialization()
    table7_verifiers()
    figure4_irac_panel()
    figure_verifier_precision_recall()
    print(f"\nDone. Files in {OUT}/:")
    for p in sorted(OUT.glob("*.png")):
        print(f"  {p.name}  ({p.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
