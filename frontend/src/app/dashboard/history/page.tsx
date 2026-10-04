"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { SAMPLE_CASES, type Code } from "@/lib/sampleData";
import { usePreviewMode } from "@/components/dashboard/DashboardShell";
import { CodeBadge, EmptyState, PageHead, VerifyState } from "@/components/dashboard/DashParts";
import styles from "@/components/dashboard/dashboard.module.css";

type Filter = "all" | Code | "starred" | "flagged";

function StarIcon({ on }: { on: boolean }) {
  return (
    <svg viewBox="0 0 20 20" width="20" height="20" aria-hidden fill={on ? "currentColor" : "none"}>
      <path
        d="M10 2.6l2.3 4.9 5.3.7-3.9 3.7.97 5.3L10 14.6l-4.7 2.6.97-5.3L2.4 8.2l5.3-.7z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function HistoryPage() {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);
  const mode = usePreviewMode();
  const [q, setQ] = useState("");
  const [filter, setFilter] = useState<Filter>("all");
  /** Starred state is local to this page for now. */
  const [starred, setStarred] = useState<Set<string>>(new Set());
  const toggleStar = (id: string) =>
    setStarred((s) => {
      const n = new Set(s);
      if (n.has(id)) n.delete(id);
      else n.add(id);
      return n;
    });

  const all = mode === "empty" ? [] : SAMPLE_CASES;
  const rows = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return all.filter((c) => {
      const passFilter =
        filter === "all" ||
        (filter === "starred"
          ? starred.has(c.id)
          : filter === "flagged"
            ? c.flagged
            : c.code === filter);
      const passSearch =
        !needle ||
        `${c.code} ${c.section} ${c.title} ${c.question}`.toLowerCase().includes(needle);
      return passFilter && passSearch;
    });
  }, [all, q, filter, starred]);

  const options: { id: Filter; label: string }[] = [
    { id: "all", label: C.fAll },
    { id: "IPC", label: C.fIpc },
    { id: "BNS", label: C.fBns },
    { id: "starred", label: C.fStarred },
    { id: "flagged", label: C.fFlagged },
  ];

  const emptyTitle =
    filter === "starred" && !q.trim()
      ? C.hiStarEmptyTitle
      : filter === "flagged" && !q.trim()
        ? C.hiFlagEmptyTitle
        : C.hiNoMatchTitle;
  const emptyBody =
    filter === "starred" && !q.trim()
      ? C.hiStarEmptyBody
      : filter === "flagged" && !q.trim()
        ? C.hiFlagEmptyBody
        : C.hiNoMatchBody;

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
              title={emptyTitle}
              body={emptyBody}
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
                    <th scope="col">
                      <span className="sr-only">{C.colStar}</span>
                    </th>
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
                  {rows.map((c, i) => (
                    <tr key={c.id} style={{ ["--i" as string]: i }}>
                      <td className={styles.starCell}>
                        <button
                          type="button"
                          className={starred.has(c.id) ? styles.starOn : styles.starOff}
                          aria-pressed={starred.has(c.id)}
                          aria-label={
                            starred.has(c.id)
                              ? C.unstar(c.code + " " + c.section)
                              : C.star(c.code + " " + c.section)
                          }
                          onClick={() => toggleStar(c.id)}
                        >
                          <StarIcon on={starred.has(c.id)} />
                        </button>
                      </td>
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
