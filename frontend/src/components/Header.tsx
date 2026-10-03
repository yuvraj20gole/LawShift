"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ScrollProgress } from "./ScrollProgress";
import { usePrefs, type Lang } from "@/lib/prefs";
import { getLandingCopy } from "@/lib/landingCopy";
import styles from "./Header.module.css";

const LANGS: { code: Lang; label: string; name: string }[] = [
  { code: "en", label: "EN", name: "English" },
  { code: "hi", label: "HI", name: "Hindi" },
  { code: "mr", label: "MR", name: "Marathi" },
];

export function Header() {
  const { lang, setLang } = usePrefs();
  const L = getLandingCopy(lang);
  const [active, setActive] = useState<"how" | "evidence" | null>(null);

  /** Mark the nav link for the section currently crossing the middle of the screen. */
  useEffect(() => {
    const map: Record<string, "how" | "evidence" | null> = {
      how: "how",
      compare: "how",
      checks: "evidence",
      evidence: "evidence",
      chat: null,
      limits: null,
    };
    const els = Object.keys(map)
      .map((id) => document.getElementById(id))
      .filter((e): e is HTMLElement => !!e);
    if (!els.length || typeof IntersectionObserver === "undefined") return;
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) setActive(map[e.target.id] ?? null);
        }
      },
      { rootMargin: "-40% 0px -55% 0px" },
    );
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);

  return (
    <header className={styles.header}>
      <ScrollProgress />
      <div className={`container ${styles.inner}`}>
        <Link href="/" className={styles.wordmark}>
          LawShift
        </Link>

        <nav className={styles.links} aria-label="Primary">
          <Link
            href="/#how"
            className={active === "how" ? styles.navLinkActive : styles.navLink}
            aria-current={active === "how" ? "location" : undefined}
          >
            {L.navHow}
          </Link>
          <Link
            href="/#evidence"
            className={active === "evidence" ? styles.navLinkActive : styles.navLink}
            aria-current={active === "evidence" ? "location" : undefined}
          >
            {L.navEvidence}
          </Link>
          <Link href="/about" className={styles.navLink}>
            {L.navAbout}
          </Link>
        </nav>

        <div className={styles.actions}>
          <div className={styles.langWrap}>
            <span className={styles.langLabel} id="answer-lang">
              {L.answersIn}
            </span>
            <div className={styles.langGroup} role="group" aria-labelledby="answer-lang">
              {LANGS.map((l) => (
                <button
                  key={l.code}
                  type="button"
                  className={lang === l.code ? styles.langActive : styles.langBtn}
                  onClick={() => setLang(l.code)}
                  aria-pressed={lang === l.code}
                  aria-label={l.name}
                  title={l.name}
                >
                  {l.label}
                </button>
              ))}
            </div>
          </div>

          <Link href="/#chat" className={styles.tryBtn}>
            {L.tryACase}
          </Link>
        </div>
      </div>
    </header>
  );
}
