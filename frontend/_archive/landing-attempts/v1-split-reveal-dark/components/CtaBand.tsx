"use client";

import Link from "next/link";
import { useT } from "@/lib/prefs";
import styles from "./CtaBand.module.css";

export function CtaBand() {
  const t = useT();
  return (
    <section className={styles.band} aria-label="Call to action">
      <div className={`container ${styles.inner}`}>
        <div className={styles.copy}>
          <h2 className={styles.heading}>{t.heroSupport}</h2>
          <p className={styles.lede}>{t.chatLede}</p>
        </div>
        <Link href="#chat" className={styles.cta}>
          {t.heroCta}
        </Link>
      </div>
    </section>
  );
}
