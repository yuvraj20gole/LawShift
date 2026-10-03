"use client";

import { useInView } from "@/hooks/useInView";
import { CountUp } from "./CountUp";
import styles from "./Viz.module.css";

type Props = {
  /** Cells filled out of 100. */
  hit: number;
  label: string;
  figure: string;
  hitLabel: string;
  missLabel: string;
};

/**
 * 10 x 10 waffle: one cell per 100 questions. Filled vs hollow carries the
 * meaning, so colour is never the only signal; the figure and legend repeat
 * it in words.
 */
export function Waffle({ hit, label, figure, hitLabel, missLabel }: Props) {
  const { ref, pending } = useInView<HTMLElement>(0.3);
  return (
    <figure ref={ref} className={`${styles.waffle} ${pending ? styles.pending : ""}`}>
      <div
        className={styles.waffleGrid}
        role="img"
        aria-label={`${label}: ${figure}. ${hitLabel}.`}
      >
        {Array.from({ length: 100 }, (_, i) => (
          <span
            key={i}
            className={i < hit ? styles.cellHit : styles.cellMiss}
            style={{ ["--n" as string]: i }}
          />
        ))}
      </div>
      <figcaption>
        <strong className={styles.figure}>
          <CountUp text={figure} />
        </strong>
        <span className={styles.vizLabel}>{label}</span>
        <span className={styles.legend}>
          <span className={styles.legendItem}>
            <i className={styles.cellHit} aria-hidden />
            {hitLabel}
          </span>
          <span className={styles.legendItem}>
            <i className={styles.cellMiss} aria-hidden />
            {missLabel}
          </span>
        </span>
      </figcaption>
    </figure>
  );
}
