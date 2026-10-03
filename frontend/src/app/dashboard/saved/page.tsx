"use client";

import { useState } from "react";
import Link from "next/link";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { SAMPLE_SAVED } from "@/lib/sampleData";
import { usePreviewMode } from "@/components/dashboard/DashboardShell";
import { CodeBadge, EmptyState, PageHead } from "@/components/dashboard/DashParts";
import { FlagIcon } from "@/components/auth/AuthParts";
import styles from "@/components/dashboard/dashboard.module.css";

export default function SavedPage() {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);
  const mode = usePreviewMode();
  const [items, setItems] = useState(mode === "empty" ? [] : SAMPLE_SAVED);
  const [confirming, setConfirming] = useState<string | null>(null);

  return (
    <>
      <PageHead title={C.svTitle} lede={C.svLede} />
      {items.length === 0 ? (
        <EmptyState
          title={C.svEmptyTitle}
          body={C.svEmptyBody}
          action={{ label: C.describeCase, href: "/dashboard/workspace" }}
        />
      ) : (
        <ul className={styles.saved}>
          {items.map((s) => {
            const label = `${s.code} ${s.section}`;
            const asking = confirming === s.id;
            return (
              <li key={s.id} className={styles.savedItem}>
                <div className={styles.savedHead}>
                  <CodeBadge code={s.code} />
                  <strong className={styles.secNum}>{s.section}</strong>
                  <span className={styles.savedTitle}>{s.title}</span>
                </div>
                <p className={styles.excerpt}>{s.excerpt}</p>
                <div className={styles.savedMeta}>
                  <span>{C.svSaved(s.saved)}</span>
                  <span className={styles.actions}>
                    <Link href="/dashboard/workspace" className={styles.linkBtn}>
                      {C.open}
                      <span className="sr-only"> {label}</span>
                    </Link>
                    <button
                      type="button"
                      className={styles.removeBtn}
                      aria-expanded={asking}
                      onClick={() => setConfirming(asking ? null : s.id)}
                    >
                      {C.remove}
                      <span className="sr-only"> {label}</span>
                    </button>
                  </span>
                </div>
                {asking ? (
                  <div className={styles.confirm} role="alertdialog" aria-label={C.svRemoveAsk(label)}>
                    <p className={styles.confirmTitle}>
                      <span className={styles.mark}>
                        <FlagIcon />
                      </span>
                      {C.svRemoveAsk(label)}
                    </p>
                    <p className={styles.confirmBody}>{C.svRemoveBody}</p>
                    <span className={styles.actions}>
                      <button
                        type="button"
                        className={styles.dangerBtn}
                        onClick={() => {
                          setItems((x) => x.filter((i) => i.id !== s.id));
                          setConfirming(null);
                        }}
                      >
                        {C.remove}
                      </button>
                      <button type="button" className={styles.secondary} onClick={() => setConfirming(null)} autoFocus>
                        {C.keep}
                      </button>
                    </span>
                  </div>
                ) : null}
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
}
