import Link from "next/link";
import { Header } from "@/components/Header";
import styles from "./about.module.css";

export const metadata = {
  title: "About — LawShift",
  description: "Evaluation sources and architectural notes for LawShift.",
};

export default function AboutPage() {
  return (
    <>
      <Header />
      <main className={styles.main}>
        <div className="container">
          <p className={styles.back}>
            <Link href="/">
              <span aria-hidden>←</span> LawShift
            </Link>
          </p>
        </div>
        <div className={`container ${styles.narrow}`}>
          <h1 className={styles.h1}>About the numbers</h1>
          <p className={styles.lede}>
            Evaluation claims are tied to held-out artifacts in this repository — not invented
            benchmarks.
          </p>

          <blockquote className={styles.pullquote}>
            <p>
              Decisions influenced by fabricated or hallucinated precedents cannot stand —
              AI may assist legal research, but it cannot replace verification.
            </p>
            <cite>
              Pooja Ramesh Singh v. Jammu &amp; Kashmir Bank Ltd., Supreme Court of India (2026)
            </cite>
          </blockquote>

          <section className={styles.block}>
            <h2>100% routing accuracy (by construction)</h2>
            <p>
              Stage 2 compares the extracted offense date to the 1 July 2024 cutoff. On the 460-row
              end-to-end set, routing accuracy is 100% by construction because the gold route is
              derived from that same date rule (<code>PROCESS_LOG.md</code> §14). This is an
              architectural guarantee, not a learned score.
            </p>
          </section>

          <section className={styles.block}>
            <h2>0.841 Recall@5</h2>
            <p>
              Selected model test metrics from{" "}
              <code>results/final_selected_model_test_eval.json</code> (n=636, k=5): Recall@5
              0.8412, MRR 0.6547, NDCG@5 0.7016 — reported as 0.841 in project summaries.
            </p>
          </section>

          <section className={styles.block}>
            <h2>0 fabricated citations / 40 generations</h2>
            <p>
              Stage 4 constrained IRAC evaluation on gold statute chunks reported zero hallucination
              of section numbers or citations across 40 cases (<code>PROCESS_LOG.md</code> §16).
              Logical consistency failures are a separate category and are what the Rule-only
              verifier targets.
            </p>
          </section>

          <section className={styles.block}>
            <h2>Data & models</h2>
            <p>
              GSMS-B statutes and QA, nandhakumarg IPC↔BNS mapping, GovIntel legal dataset,
              nyaya-eval-v0 external validation, AI4Bharat IndicTrans2 for optional Hindi/Marathi
              IRAC translation. Retrieval: fine-tuned bge-small epoch-8 checkpoint.
            </p>
          </section>

          <p className={styles.disclaimer}>
            LawShift is an informational tool, not legal advice.
          </p>
        </div>
      </main>
    </>
  );
}
