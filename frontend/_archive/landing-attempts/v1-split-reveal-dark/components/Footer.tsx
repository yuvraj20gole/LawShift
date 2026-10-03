"use client";

import Link from "next/link";
import { useT } from "@/lib/prefs";
import styles from "./Footer.module.css";

export function Footer() {
  const t = useT();
  return (
    <footer className={styles.footer}>
      <div className={`container ${styles.inner}`}>
        <div className={styles.credits}>
          <p className={styles.brand}>LawShift</p>
          <p className={styles.meta}>{t.footerMeta}</p>
        </div>
        <div className={styles.links}>
          <Link href="/about">{t.about}</Link>
        </div>
      </div>
      <div className="container">
        <p className={styles.disclaimer}>{t.footerDisclaimer}</p>
      </div>
    </footer>
  );
}
