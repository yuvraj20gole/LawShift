"use client";

import { useRef } from "react";
import {
  motion,
  useReducedMotion,
  useScroll,
  useTransform,
} from "framer-motion";
import styles from "./ProductPreview.module.css";

/**
 * Framed mid-conversation snapshot of the real LawShift chat UI —
 * mapping card, IRAC fields, Sources, quiet verification check.
 * Decorative (aria-hidden); the live workspace lives further down the page.
 */
export function ProductPreview() {
  const reduce = useReducedMotion();
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });
  const y = useTransform(scrollYProgress, [0, 1], reduce ? [0, 0] : [32, -40]);
  const rotate = useTransform(
    scrollYProgress,
    [0, 1],
    reduce ? [-1.15, -1.15] : [-2.4, 0.8],
  );

  return (
    <div ref={ref} className={styles.parallax} aria-hidden="true">
      <motion.div className={styles.frame} style={{ y, rotate }}>
        <div className={styles.chrome}>
          <span className={styles.dot} />
          <span className={styles.dot} />
          <span className={styles.dot} />
          <span className={styles.chromeTitle}>LawShift workspace</span>
        </div>

        <div className={styles.body}>
          <div className={styles.msg}>
            <span className={styles.role}>You</span>
            <p className={styles.userText}>
              On 5 September 2024, a person was found in possession of counterfeit
              currency notes.
            </p>
          </div>

          <div className={styles.msg}>
            <span className={styles.role}>LawShift</span>
            <p className={styles.summary}>
              Mapped · <span className={styles.sectionBadge}>BNS 180</span>
            </p>

            <div className={styles.irac}>
              <div className={styles.field}>
                <span className={styles.label}>Issue</span>
                <p>
                  Which BNS provision governs possession of counterfeit currency on
                  5 September 2024?
                </p>
              </div>
              <div className={styles.field}>
                <span className={styles.label}>Rule</span>
                <p>
                  BNS 180 punishes possession of counterfeit coin or currency notes
                  knowing them to be counterfeit, intending to use them as genuine.
                </p>
              </div>
              <div className={styles.field}>
                <span className={styles.label}>Application</span>
                <p>
                  The offence date falls on or after 1 July 2024, so BNS applies. The
                  facts describe knowing possession of counterfeit notes.
                </p>
              </div>
              <div className={styles.field}>
                <span className={styles.label}>Conclusion</span>
                <p>BNS Section 180 is the governing provision.</p>
              </div>
            </div>

            <div className={styles.sources}>
              <p className={styles.sourcesHead}>Sources (1)</p>
              <div className={styles.sourceRow}>
                <strong>BNS · 180</strong>
                <span>Show statute text</span>
              </div>
            </div>

            <div className={styles.verify}>
              <span className={styles.check} aria-hidden>
                ✓
              </span>
              <span>No inconsistency detected</span>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
