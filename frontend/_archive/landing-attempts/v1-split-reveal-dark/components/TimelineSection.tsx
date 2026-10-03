"use client";

import { EraTimeline } from "./EraTimeline";
import styles from "./TimelineSection.module.css";

export function TimelineSection() {
  return (
    <section className={`${styles.section} section-alt`} aria-label="IPC to BNS transition timeline">
      <div className={styles.inner}>
        <p className={styles.kicker}>The cutoff that decides which code governs</p>
        <h2 className={styles.heading}>
          From IPC to BNS — one date, not a model guess
        </h2>
        <div className={styles.timeline}>
          <EraTimeline variant="section" />
        </div>
      </div>
    </section>
  );
}
