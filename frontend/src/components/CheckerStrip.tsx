"use client";

import { useInView } from "@/hooks/useInView";
import styles from "./Viz.module.css";

type Props = {
  title: string;
  caught: string;
  falseAlarm: string;
  clear: string;
};

/**
 * The 40 hand-read answers (PROCESS_LOG §17): 5 had a conclusion that did not
 * follow the rule, and the checker flagged all 5. It also flagged 10 good
 * answers, and left 25 alone. Three cell treatments (solid, hatched, hollow)
 * so the split reads without colour.
 */
export function CheckerStrip({ title, caught, falseAlarm, clear }: Props) {
  type Kind = "caught" | "false" | "clear";
  const cells: Kind[] = [
    ...Array<Kind>(5).fill("caught"),
    ...Array<Kind>(10).fill("false"),
    ...Array<Kind>(25).fill("clear"),
  ];
  const cls: Record<Kind, string> = { caught: styles.stripCaught, false: styles.stripFalse, clear: styles.stripClear };

  const { ref, pending } = useInView<HTMLElement>(0.3);

  return (
    <figure ref={ref} className={`${styles.strip} ${pending ? styles.pending : ""}`}>
      <figcaption className={styles.stripTitle}>{title}</figcaption>
      <div
        className={styles.stripGrid}
        role="img"
        aria-label={`${title}. ${caught}. ${falseAlarm}. ${clear}.`}
      >
        {cells.map((k, i) => (
          <span key={i} className={cls[k]} style={{ ["--n" as string]: i }} />
        ))}
      </div>
      <ul className={styles.stripLegend}>
        <li>
          <i className={styles.stripCaught} aria-hidden />
          {caught}
        </li>
        <li>
          <i className={styles.stripFalse} aria-hidden />
          {falseAlarm}
        </li>
        <li>
          <i className={styles.stripClear} aria-hidden />
          {clear}
        </li>
      </ul>
    </figure>
  );
}
