"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { createClient } from "@/lib/supabase/client";
import { openingText, type CaseRow } from "@/lib/caseHistory";
import { CodeBadge, EmptyState, PageHead, VerifyState } from "@/components/dashboard/DashParts";
import { FlagIcon } from "@/components/auth/AuthParts";
import styles from "@/components/dashboard/dashboard.module.css";

type Filter = "all" | "IPC" | "BNS" | "starred" | "flagged";
type Load = "loading" | "error" | "ready";

const LOCALES = { en: "en-GB", hi: "hi-IN", mr: "mr-IN" } as const;

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
  const router = useRouter();
  const [all, setAll] = useState<CaseRow[]>([]);
  const [load, setLoad] = useState<Load>("loading");
  const [q, setQ] = useState("");
  const [filter, setFilter] = useState<Filter>("all");
  const [actionError, setActionError] = useState(false);
  const [confirmClear, setConfirmClear] = useState(false);

  const fetchRows = useCallback(async () => {
    setLoad("loading");
    try {
      const { data, error } = await createClient()
        .from("case_history")
        .select("id,created_at,question,offence_date,code,section,heading,flagged,starred,language")
        .order("created_at", { ascending: false })
        .limit(1000);
      if (error) throw error;
      setAll((data ?? []) as CaseRow[]);
      setLoad("ready");
    } catch {
      setLoad("error");
    }
  }, []);

  useEffect(() => {
    void fetchRows();
  }, [fetchRows]);

  const fmtDay = (iso: string, utc: boolean) =>
    new Date(iso).toLocaleDateString(LOCALES[lang] ?? "en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
      ...(utc ? { timeZone: "UTC" } : {}),
    });

  async function toggleStar(row: CaseRow) {
    const next = !row.starred;
    setActionError(false);
    setAll((rs) => rs.map((r) => (r.id === row.id ? { ...r, starred: next } : r)));
    const { error } = await createClient().from("case_history").update({ starred: next }).eq("id", row.id);
    if (error) {
      setAll((rs) => rs.map((r) => (r.id === row.id ? { ...r, starred: row.starred } : r)));
      setActionError(true);
    }
  }

  async function removeRow(row: CaseRow) {
    setActionError(false);
    const { error } = await createClient().from("case_history").delete().eq("id", row.id);
    if (error) setActionError(true);
    else setAll((rs) => rs.filter((r) => r.id !== row.id));
  }

  async function clearAll() {
    setActionError(false);
    const { error } = await createClient().from("case_history").delete().not("id", "is", null);
    setConfirmClear(false);
    if (error) setActionError(true);
    else setAll([]);
  }

  function openRow(row: CaseRow) {
    try {
      sessionStorage.setItem("lawshift-carry", openingText(row.question, row.offence_date));
      sessionStorage.setItem("lawshift-open", row.id);
    } catch {
      /* the Workspace just opens empty */
    }
    router.push("/dashboard/workspace");
  }

  const rows = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return all.filter((c) => {
      const passFilter =
        filter === "all" ||
        (filter === "starred" ? c.starred : filter === "flagged" ? c.flagged : c.code === filter);
      const passSearch =
        !needle || `${c.code} ${c.section} ${c.heading ?? ""} ${c.question}`.toLowerCase().includes(needle);
      return passFilter && passSearch;
    });
  }, [all, q, filter]);

  const options: { id: Filter; label: string }[] = [
    { id: "all", label: C.fAll },
    { id: "IPC", label: C.fIpc },
    { id: "BNS", label: C.fBns },
    { id: "starred", label: C.fStarred },
    { id: "flagged", label: C.fFlagged },
  ];

  const plain = !q.trim();
  const emptyTitle =
    filter === "starred" && plain ? C.hiStarEmptyTitle : filter === "flagged" && plain ? C.hiFlagEmptyTitle : C.hiNoMatchTitle;
  const emptyBody =
    filter === "starred" && plain ? C.hiStarEmptyBody : filter === "flagged" && plain ? C.hiFlagEmptyBody : C.hiNoMatchBody;

  return (
    <>
      <PageHead title={C.hiTitle} lede={C.hiLede} />
      <p className={styles.savedNote}>{C.hiSavedNote}</p>

      {load === "loading" ? (
        <p className={styles.loadingLine} role="status">
          {C.hiLoading}
        </p>
      ) : load === "error" ? (
        <EmptyState title={C.hiError} body="" action={{ label: C.hiRetry, onClick: () => void fetchRows() }} />
      ) : all.length === 0 ? (
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

          {actionError ? (
            <p className={styles.flagNote} role="alert">
              <span className={styles.mark}>
                <FlagIcon />
              </span>
              {C.hiActionFailed}
            </p>
          ) : null}

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
                  {rows.map((c, i) => {
                    const label = `${c.code} ${c.section}`;
                    return (
                      <tr key={c.id} style={{ ["--i" as string]: i }}>
                        <td className={styles.starCell}>
                          <button
                            type="button"
                            className={c.starred ? styles.starOn : styles.starOff}
                            aria-pressed={c.starred}
                            aria-label={c.starred ? C.unstar(label) : C.star(label)}
                            onClick={() => void toggleStar(c)}
                          >
                            <StarIcon on={c.starred} />
                          </button>
                        </td>
                        <td data-label={C.colAsked}>{fmtDay(c.created_at, false)}</td>
                        <td data-label={C.colOffence}>{c.offence_date ? fmtDay(c.offence_date, true) : "—"}</td>
                        <td data-label={C.colCode}>
                          <CodeBadge code={c.code} />
                        </td>
                        <td data-label={C.colSection}>
                          <div>
                            <strong className={styles.secNum}>{c.section}</strong>
                            {c.heading ? <span className={styles.secTitle}>{c.heading}</span> : null}
                            <span className={styles.secQuestion}>{c.question}</span>
                          </div>
                        </td>
                        <td data-label={C.colState}>
                          <VerifyState flagged={c.flagged} okText={C.verOk} flagText={C.verFlag} />
                        </td>
                        <td>
                          <div className={styles.rowActions}>
                            <button type="button" className={styles.linkBtn} onClick={() => openRow(c)}>
                              {C.open}
                              <span className="sr-only"> {label}</span>
                            </button>
                            <button type="button" className={styles.rowDelete} onClick={() => void removeRow(c)}>
                              {C.hiDelete}
                              <span className="sr-only"> {label}</span>
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          <div className={styles.clearRow}>
            {confirmClear ? (
              <div className={styles.confirm} role="alertdialog" aria-labelledby="clear-title">
                <p id="clear-title" className={styles.confirmTitle}>
                  <FlagIcon />
                  {C.hiClearTitle}
                </p>
                <p className={styles.confirmBody}>{C.hiClearBody}</p>
                <div className={styles.confirmActions}>
                  <button type="button" className={styles.dangerBtn} onClick={() => void clearAll()}>
                    {C.hiClearConfirm}
                  </button>
                  <button type="button" className={styles.secondary} onClick={() => setConfirmClear(false)}>
                    {C.hiCancel}
                  </button>
                </div>
              </div>
            ) : (
              <button type="button" className={styles.rowDelete} onClick={() => setConfirmClear(true)}>
                {C.hiClearAll}
              </button>
            )}
          </div>
        </>
      )}
    </>
  );
}
