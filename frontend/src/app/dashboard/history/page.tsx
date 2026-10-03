"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { SAMPLE_CASES, type Code } from "@/lib/sampleData";
import { usePreviewMode } from "@/components/dashboard/DashboardShell";
import { CodeBadge, EmptyState, PageHead, VerifyState } from "@/components/dashboard/DashParts";
import styles from "@/components/dashboard/dashboard.module.css";

type Filter = "all" | Code;

export default function HistoryPage() {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);
  const mode = usePreviewMode();
  const [q, setQ] = useState("");
  const [filter, setFilter] = useState<Filter>("all");

  const all = mode === "empty" ? [] : SAMPLE_CASES;
  const rows = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return all.filter(
      (c) =>
        (filter === "all" || c.code === filter) &&
        (!needle ||
          `${c.code} ${c.section} ${c.title} ${c.question}`.toLowerCase().includes(needle)),
    );
  }, [all, q, filter]);

  const options: { id: Filter; label: string }[] = [
    { id: "all", label: C.fAll },
    { id: "IPC", label: C.fIpc },
    { id: "BNS", label: C.fBns },
  ];

  return (
    <>
      <PageHead title={C.hiTitle} lede={C.hiLede} />

      {all.length === 0 ? (
        <EmptyState
          title={C.hiEmptyTitle}
          body={C.hiEmptyBody}
          action={{ label: C.describeCase, href: "/dashboard/workspace" }}
        />
      ) : (
        <>
          <div className={styles.toolbar}>
            <div className={styles.search}>
              <label htmlFor="case-search" className={styles.toolLabel}>
                {C.hiSearch}
              </label>
              <input
                id="case-search"
                type="search"
                className={styles.searchInput}
                placeholder={C.hiSearchHint}
                value={q}
                onChange={(e) => setQ(e.target.value)}
              />
            </div>
            <div className={styles.filterWrap}>
              <span className={styles.toolLabel} id="code-filter">
                {C.hiFilter}
              </span>
              <div role="radiogroup" aria-labelledby="code-filter" className={styles.segGroup}>
                {options.map((o) => (
                  <button
                    key={o.id}
                    type="button"
                    role="radio"
                    aria-checked={filter === o.id}
                    className={filter === o.id ? styles.segOn : styles.seg}
                    onClick={() => setFilter(o.id)}
                  >
                    {o.label}
                  </button>
                ))}
              </div>
            </div>
            <p className={styles.count} aria-live="polite">
              {C.hiCount(rows.length)}
            </p>
          </div>

          {rows.length === 0 ? (
            <EmptyState
              title={C.hiNoMatchTitle}
              body={C.hiNoMatchBody}
              action={{
                label: C.clearFilters,
                onClick: () => {
                  setQ("");
                  setFilter("all");
                },
              }}
            />
          ) : (
            <div className={styles.tableWrap}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th scope="col">{C.colAsked}</th>
                    <th scope="col">{C.colOffence}</th>
                    <th scope="col">{C.colCode}</th>
                    <th scope="col">{C.colSection}</th>
                    <th scope="col">{C.colState}</th>
                    <th scope="col">
                      <span className="sr-only">{C.colAction}</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((c) => (
                    <tr key={c.id}>
                      <td data-label={C.colAsked}>{c.asked}</td>
                      <td data-label={C.colOffence}>{c.offence}</td>
                      <td data-label={C.colCode}>
                        <CodeBadge code={c.code} />
                      </td>
                      <td data-label={C.colSection}>
                        <strong className={styles.secNum}>{c.section}</strong>
                        <span className={styles.secTitle}>{c.title}</span>
                      </td>
                      <td data-label={C.colState}>
                        <VerifyState flagged={c.flagged} okText={C.verOk} flagText={C.verFlag} />
                      </td>
                      <td>
                        <Link href="/dashboard/workspace" className={styles.linkBtn}>
                          {C.open}
                          <span className="sr-only">
                            {" "}
                            {c.code} {c.section}
                          </span>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </>
  );
}
