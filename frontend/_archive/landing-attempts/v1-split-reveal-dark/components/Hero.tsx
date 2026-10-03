"use client";

import Link from "next/link";
import { IPC_BACKDROP, BNS_BACKDROP } from "@/lib/statuteBackdrop";
import { useT } from "@/lib/prefs";
import styles from "./Hero.module.css";

export function Hero() {
  const t = useT();
  return (
    <section className={styles.hero} aria-labelledby="hero-headline">
      <div className={styles.split} aria-hidden="true">
        <div className={styles.halfIpc}>
          <pre className={styles.statuteText}>{IPC_BACKDROP}</pre>
          <span className={styles.eraLabel}>IPC 1860</span>
        </div>
        <div className={styles.halfBns}>
          <pre className={styles.statuteText}>{BNS_BACKDROP}</pre>
          <span className={styles.eraLabelBns}>BNS 2023</span>
        </div>
        <div className={styles.divider} />
      </div>

      <div className={`container ${styles.foreground}`}>
        <div className={styles.copy}>
          <h1 id="hero-headline" className={styles.headline}>
            {t.heroHeadline}
          </h1>
          <p className={styles.support}>{t.heroSupport}</p>
          <div className={styles.ctaRow}>
            <Link href="#chat" className={styles.cta}>
              {t.heroCta}
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
