"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { Header } from "@/components/Header";
import { usePrefs } from "@/lib/prefs";
import { getLandingCopy } from "@/lib/landingCopy";
import { getAuthCopy } from "@/lib/authCopy";
import { SHOW_SAMPLE_SIGNS } from "@/lib/showSampleSigns";
import styles from "./auth.module.css";

/** Shared frame: header, the navy panel with the cutoff motif, and the form card. */
export function AuthShell({
  title,
  lede,
  children,
}: {
  title: string;
  lede: string;
  children: ReactNode;
}) {
  const { lang } = usePrefs();
  const L = getLandingCopy(lang);
  const A = getAuthCopy(lang);

  return (
    <>
      <Header minimal />
      <main id="main" className={styles.main}>
        <div className="container">
          <Link href="/" className={styles.back}>
            <span aria-hidden>←</span> {A.backHome}
          </Link>
        </div>
        <div className={`container ${styles.grid}`}>
          <aside className={styles.panel} aria-hidden>
            <p className={styles.panelTitle}>{L.heroTitle}</p>
            <div className={styles.cut}>
              <span className={styles.cutLine} />
              <span className={styles.cutPill}>1 July 2024</span>
              <span className={styles.cutLine} />
            </div>
            <div className={styles.sides}>
              <p>
                <strong>{L.docketBefore}</strong>
                <span>{L.docketIpcName}</span>
              </p>
              <p>
                <strong>{L.docketAfter}</strong>
                <span>{L.docketBnsName}</span>
              </p>
            </div>
          </aside>

          <section className={styles.card} aria-labelledby="auth-title">
            <h1 id="auth-title" className={styles.title}>
              {title}
            </h1>
            <p className={styles.lede}>{lede}</p>
            {SHOW_SAMPLE_SIGNS ? (
              <p className={styles.preview}>{A.previewNote}</p>
            ) : null}
            {children}
          </section>
        </div>
      </main>
    </>
  );
}
