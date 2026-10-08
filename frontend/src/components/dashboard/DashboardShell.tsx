"use client";

import { createContext, useContext, useState, type ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Header } from "@/components/Header";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { useSession } from "@/lib/useSession";
import { SHOW_SAMPLE_SIGNS } from "@/lib/showSampleSigns";
import styles from "./dashboard.module.css";

type Mode = "sample" | "empty";
const ModeContext = createContext<Mode>("sample");

/** Pages read this to show either the populated or the empty state. */
export function usePreviewMode() {
  return useContext(ModeContext);
}

export function DashboardShell({ children }: { children: ReactNode }) {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);
  const path = usePathname();
  const { email } = useSession();
  const [mode, setMode] = useState<Mode>("sample");
  const [menuOpen, setMenuOpen] = useState(false);

  const items = [
    { href: "/dashboard/workspace", label: C.navWorkspace },
    { href: "/dashboard/mapping", label: C.navMapping },
    { href: "/dashboard/history", label: C.navHistory },
    { href: "/dashboard/documents", label: C.navDocuments },
    { href: "/dashboard/rulings", label: C.navRulings },
    { href: "/dashboard/settings", label: C.navSettings },
  ];
  const isActive = (i: (typeof items)[number]) => path?.startsWith(i.href);
  const current = items.find(isActive) ?? items[0];
  /** Mapping and Rulings never show the strip; elsewhere gated by SHOW_SAMPLE_SIGNS. */
  const showPreview =
    SHOW_SAMPLE_SIGNS &&
    !(path?.startsWith("/dashboard/mapping") || path?.startsWith("/dashboard/rulings"));

  return (
    <>
      <Header account={{ email: email ?? "", logout: C.logout }} />
      <div className={`container ${styles.shell}`}>
        <aside className={styles.side}>
          <button
            type="button"
            className={styles.menuBtn}
            aria-expanded={menuOpen}
            aria-controls="dash-nav"
            onClick={() => setMenuOpen((o) => !o)}
          >
            <span>{C.menu}</span>
            <strong>{current.label}</strong>
          </button>
          <nav
            id="dash-nav"
            aria-label={C.navLabel}
            className={`${styles.nav} ${menuOpen ? styles.navOpen : ""}`}
          >
            {items.map((i) => (
              <Link
                key={i.href}
                href={i.href}
                className={isActive(i) ? styles.navItemOn : styles.navItem}
                aria-current={isActive(i) ? "page" : undefined}
                onClick={() => setMenuOpen(false)}
              >
                {i.label}
              </Link>
            ))}
          </nav>
        </aside>

        <main id="main" className={styles.main}>
          {showPreview ? (
          <div className={styles.preview} role="note">
            <p>{C.previewNote}</p>
            <div className={styles.previewSwitch} role="group" aria-label={C.previewShow}>
              <span>{C.previewShow}</span>
              <button
                type="button"
                aria-pressed={mode === "sample"}
                className={mode === "sample" ? styles.segOn : styles.seg}
                onClick={() => setMode("sample")}
              >
                {C.previewSample}
              </button>
              <button
                type="button"
                aria-pressed={mode === "empty"}
                className={mode === "empty" ? styles.segOn : styles.seg}
                onClick={() => setMode("empty")}
              >
                {C.previewEmpty}
              </button>
            </div>
          </div>
          ) : null}
          <ModeContext.Provider value={mode}>
            <div key={`${mode}-${path}`} className={styles.content}>
              {children}
            </div>
          </ModeContext.Provider>
        </main>
      </div>
    </>
  );
}
