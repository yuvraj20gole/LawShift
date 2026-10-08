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
              The 40 were written with the correct section supplied and read once by hand. The
              writer runs without a fixed seed, so re-running it gives different wording each
              time and fresh runs will not reproduce them. In 5 of the 40, the model-written
              conclusion did not follow from the rule.
            </p>
            <p>
              A later check of 60 answers found 5 Rules with wording not in the section text (two
              were real rewordings) and 5 Applications that mentioned a legal-test phrase the
              user did not say. The full statute text is shown under every answer.
            </p>
            <p>
              Every mapped answer now ends with a fixed Conclusion sentence written by code, not
              by the model. The larger model compares the Rule with that Conclusion. On the same
              40 answers it flags 12, where the 40-answer test above (5 bad answers, all 5 flagged,
              10 good answers flagged as well) was measured on the earlier model-written
              Conclusions. It can catch a Rule that does not match the section heading, cannot see
              whether the Application adds facts the user did not give, and is a second opinion
              that never blocks an answer.
            </p>
          </section>

          <section className={styles.block}>
            <h2>Data & models</h2>
            <p>
              GSMS-B statutes and QA (Apache 2.0), nandhakumarg IPC↔BNS mapping (Apache 2.0),
              GovIntel legal dataset (CC BY-NC 4.0), nyaya-eval-v0 external validation (CC BY
              4.0), AI4Bharat IndicTrans2 for optional Hindi/Marathi IRAC translation. Court
              judgments come from an open archive (CC BY 4.0), credited to Dattam Labs and the
              dataset maintainers. Retrieval: fine-tuned bge-small epoch-8 checkpoint.
            </p>
            <p>
              Translation runs after the legal analysis. A check compares numbers, and if
              translation changes one, that part stays in English with a note. Number words such
              as “two years” are not checked. The Hindi and Marathi Conclusion is a fixed template.
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
