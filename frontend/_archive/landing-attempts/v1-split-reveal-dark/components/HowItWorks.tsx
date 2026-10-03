"use client";

import { Reveal } from "./Reveal";
import { useT } from "@/lib/prefs";
import styles from "./HowItWorks.module.css";

const STEP_NUM_CLASS = [
  styles.numteal,
  styles.numamber,
  styles.numrose,
  styles.numgreen,
] as const;

export function HowItWorks() {
  const t = useT();

  const steps = [
    { n: "1", title: t.stepExtract, phrase: t.stepExtractPhrase },
    { n: "2", title: t.stepGate, phrase: t.stepGatePhrase },
    { n: "3", title: t.stepRetrieve, phrase: t.stepRetrievePhrase },
    { n: "4", title: t.stepSynthesize, phrase: t.stepSynthesizePhrase },
  ];

  return (
    <section className={styles.section} aria-labelledby="how-heading">
      <div className={`container ${styles.panel}`}>
        <Reveal>
          <h2 id="how-heading" className={styles.heading}>
            {t.howHeading}
          </h2>
          <p className={styles.lede}>{t.howLede}</p>
        </Reveal>

        <div className={styles.diagram} role="list">
          {steps.map((step, i) => (
            <Reveal key={step.n} index={i} className={styles.item}>
              <article className={styles.box} role="listitem">
                <span
                  className={`${styles.num} ${STEP_NUM_CLASS[i]}`}
                  aria-hidden="true"
                >
                  {step.n}
                </span>
                <p className={styles.title}>{step.title}</p>
                <p className={styles.phrase}>{step.phrase}</p>
              </article>
              {i < steps.length - 1 ? (
                <svg
                  className={styles.arrow}
                  viewBox="0 0 40 12"
                  aria-hidden="true"
                  focusable="false"
                >
                  <path
                    d="M0 6h32M28 1l8 5-8 5"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                  />
                </svg>
              ) : null}
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

