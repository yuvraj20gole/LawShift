"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { detachActiveBestEffort } from "@/lib/documents";
import { createClient } from "@/lib/supabase/client";
import { ScrollProgress } from "./ScrollProgress";
import { usePrefs, type Lang } from "@/lib/prefs";
import { getLandingCopy } from "@/lib/landingCopy";
import styles from "./Header.module.css";

const LANGS: { code: Lang; label: string; name: string }[] = [
  { code: "en", label: "EN", name: "English" },
  { code: "hi", label: "HI", name: "Hindi" },
  { code: "mr", label: "MR", name: "Marathi" },
];

/** `minimal`: wordmark and language switch only (sign-in screens). */
export function Header({
  minimal = false,
  account,
}: {
  minimal?: boolean;
  /** Signed-in view: logo to the dashboard, language switch, email, Log out. */
  account?: { email: string; logout: string };
}) {
  const { lang, setLang } = usePrefs();
  const L = getLandingCopy(lang);
  /** Signed-in and sign-in screens keep only the logo and the account controls. */
  const slim = minimal || !!account;
  const [active, setActive] = useState<"how" | "evidence" | null>(null);
  const router = useRouter();

  async function logOut() {
    try {
      // While the token is still valid: drop any attached document from this chat (waits at most 1.5 s).
      await Promise.race([detachActiveBestEffort(), new Promise((r) => setTimeout(r, 1500))]);
      await createClient().auth.signOut();
    } finally {
      router.replace("/");
      router.refresh();
    }
  }

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
      <div className={`container ${styles.inner} ${slim ? styles.innerMinimal : ""}`}>
        <Link href={account ? "/dashboard" : "/"} className={styles.wordmark}>
          LawShift
        </Link>

        {!slim ? (
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
        ) : null}

        <div className={styles.actions}>
          <div className={styles.langWrap}>
            {!slim ? (
              <span className={styles.langLabel} id="answer-lang">
                {L.answersIn}
              </span>
            ) : null}
            <div
              className={styles.langGroup}
              role="group"
              {...(slim ? { "aria-label": "Language" } : { "aria-labelledby": "answer-lang" })}
            >
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

          {account ? (
            <>
              <span className={styles.accountEmail}>{account.email}</span>
              <button type="button" className={styles.logoutBtn} onClick={logOut}>
                {account.logout}
              </button>
            </>
          ) : !minimal ? (
            <>
              <Link href="/login" className={styles.loginLink}>
                {L.navLogin}
              </Link>
              <Link href="/register" className={styles.tryBtn}>
                {L.navRegister}
              </Link>
            </>
          ) : null}
        </div>
      </div>
    </header>
  );
}
