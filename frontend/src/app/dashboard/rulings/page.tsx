"use client";

import { useEffect, useId, useMemo, useState } from "react";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy, type DashboardCopy } from "@/lib/dashboardCopy";
import { fmtDate, tidy } from "@/lib/format";
import { linkLabel } from "@/lib/rulingLinks";
import { useRulingsGroup, type ArchiveRow } from "@/lib/useRulingsGroup";
import {
  BACKGROUND_RULINGS,
  FEATURED_RULINGS,
  lastReviewed,
  visibleRulings,
  type RulingEntry,
} from "@/data/rulings";
import { BenchTip, useBenchTip } from "@/components/dashboard/BenchTip";
import { EmptyState, PageHead } from "@/components/dashboard/DashParts";
import { SHOW_SAMPLE_SIGNS } from "@/lib/showSampleSigns";
import styles from "@/components/dashboard/dashboard.module.css";

type Branch = "all" | "ipcbns" | "criminal" | "civil";
type CourtKey = "all" | "sc" | "bombay";

const SC = "Supreme Court of India";
const BOMBAY = "Bombay High Court";

function CuratedItem({ e, C }: { e: RulingEntry; C: DashboardCopy }) {
  return (
    <li className={styles.rulingItem}>
      <p className={styles.rulingMeta}>
        <span>{e.court}</span>
        <span>{e.decidedOn === "to verify" ? C.dateToVerify : fmtDate(e.decidedOn)}</span>
        {SHOW_SAMPLE_SIGNS && !e.verified ? (
          <span className={styles.draftBadge}>{C.draftBadge}</span>
        ) : null}
      </p>
      <p className={styles.rulingTitle}>{e.title}</p>
      {e.caseNumber ? <p className={styles.rulingCase}>{e.caseNumber}</p> : null}
      <p className={styles.rulingHolding}>{e.holding}</p>
      <a href={e.url} target="_blank" rel="noopener noreferrer" className={styles.linkBtn}>
        {linkLabel(C, e.linkKind, e.url, e.siteName)}
      </a>
    </li>
  );
}

function ScItem({ r, C }: { r: ArchiveRow; C: DashboardCopy }) {
  return (
    <li className={styles.rulingItem}>
      <p className={styles.rulingMeta}>
        <span>{fmtDate(r.decidedOn)}</span>
        {r.caseNumber ? <span>{r.caseNumber}</span> : null}
        {r.caseType ? <span>{r.caseType}</span> : null}
      </p>
      <p className={styles.rulingTitle}>{tidy(r.title ?? "")}</p>
      <a href={r.link} target="_blank" rel="noopener noreferrer" className={styles.linkBtn}>
        {linkLabel(C, r.linkKind, r.link)}
      </a>
    </li>
  );
}

/** Bombay entries carry no party names: case type, number, bench, date and outcome only. */
function BombayItem({ r, C }: { r: ArchiveRow; C: DashboardCopy }) {
  return (
    <li className={styles.bombayItem}>
      <span className={styles.bCell} data-label={C.rlCaseNumber}>
        <strong className={styles.bNum}>{r.caseNumber ?? "—"}</strong>
        <span className={styles.bType}>{r.caseType}</span>
      </span>
      <span className={styles.bCell} data-label={C.rlBenchCol}>
        {r.bench ? <BenchTip code={r.bench} label={r.benchLabel} /> : "—"}
      </span>
      <span className={styles.bCell} data-label={C.rlDecided}>
        {fmtDate(r.decidedOn)}
      </span>
      <span className={styles.bCell} data-label={C.rlOutcome}>
        {r.disposalOutcome ?? "—"}
      </span>
      <a href={r.link} target="_blank" rel="noopener noreferrer" className={styles.linkBtn}>
        {linkLabel(C, r.linkKind, r.link)}
      </a>
    </li>
  );
}

export default function RulingsPage() {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);

  const [branch, setBranch] = useState<Branch>("all");
  const [court, setCourt] = useState<CourtKey>("all");
  const [bench, setBench] = useState<string | null>(null);
  const [qInput, setQInput] = useState("");
  const [q, setQ] = useState("");

  useEffect(() => {
    const t = setTimeout(() => setQ(qInput.trim()), 250);
    return () => clearTimeout(t);
  }, [qInput]);

  const apiBranch = branch === "criminal" || branch === "civil" ? branch : undefined;
  const archiveOn = branch !== "ipcbns";

  const sc = useRulingsGroup({
    court: SC,
    branch: apiBranch,
    q,
    enabled: archiveOn && (court === "all" || court === "sc"),
  });
  const bombay = useRulingsGroup({
    court: BOMBAY,
    branch: apiBranch,
    q,
    bench: court === "bombay" ? bench : null,
    enabled: archiveOn && (court === "all" || court === "bombay"),
  });

  // Curated entries (rulings.ts), filtered the same way as the archive.
  const curatedAll = useMemo(() => visibleRulings([...BACKGROUND_RULINGS, ...FEATURED_RULINGS]), []);
  const curated = useMemo(() => {
    const needle = q.toLowerCase();
    return curatedAll.filter((e) => {
      const okBranch =
        branch === "all" ? true : branch === "ipcbns" ? e.topic === "ipc-bns" : e.branch === branch;
      const okCourt =
        court === "all" ||
        (court === "sc" && e.court.includes("Supreme")) ||
        (court === "bombay" && e.court.includes("Bombay"));
      const okQ = !needle || `${e.title} ${e.caseNumber ?? ""}`.toLowerCase().includes(needle);
      return okBranch && okCourt && okQ;
    });
  }, [curatedAll, branch, court, q]);
  const background = curated.filter((e) => e.group === "background");
  const featured = curated.filter((e) => e.group === "featured");
  const reviewed = lastReviewed(curatedAll);

  const filtersOn = branch !== "all" || court !== "all" || q !== "";
  const loading = sc.status === "loading" || bombay.status === "loading";
  const nothing =
    !loading &&
    curated.length === 0 &&
    sc.rows.length === 0 &&
    bombay.rows.length === 0 &&
    sc.status !== "failed" &&
    bombay.status !== "failed";

  function clearAll() {
    setBranch("all");
    setCourt("all");
    setBench(null);
    setQInput("");
    setQ("");
  }

  const branches: { id: Branch; label: string }[] = [
    { id: "all", label: C.bAll },
    { id: "ipcbns", label: C.bIpcBns },
    { id: "criminal", label: C.bCriminal },
    { id: "civil", label: C.bCivil },
  ];
  const courts: { id: CourtKey; label: string }[] = [
    { id: "all", label: C.cAll },
    { id: "sc", label: C.cSupreme },
    { id: "bombay", label: C.cBombay },
  ];

  const archiveNotes = (meta: { newestRecordDate?: string } | null, sample: string | null) =>
    meta ? (
      <div className={styles.groupNotes}>
        {meta.newestRecordDate ? (
          <p>
            {C.rlCurrentTo(fmtDate(meta.newestRecordDate))}. {C.rlBatches}
          </p>
        ) : null}
        {sample ? <p>{sample}</p> : null}
        <p>{C.rlAttribution}</p>
      </div>
    ) : null;

  return (
    <>
      <PageHead title={C.rulTitle} lede={C.rlLede} />

      <div className={styles.rlFilters}>
        <div className={styles.search}>
          <label htmlFor="rl-search" className={styles.toolLabel}>
            {C.rlSearch}
          </label>
          <input
            id="rl-search"
            type="search"
            className={styles.searchInput}
            placeholder={C.rlSearchHint}
            value={qInput}
            onChange={(e) => setQInput(e.target.value)}
          />
        </div>

        <div className={styles.chipBlock}>
          <span className={styles.toolLabel} id="rl-branch">
            {C.rlBranch}
          </span>
          <div role="group" aria-labelledby="rl-branch" className={styles.chipRowF}>
            {branches.map((b) => (
              <button
                key={b.id}
                type="button"
                aria-pressed={branch === b.id}
                className={branch === b.id ? styles.fchipOn : styles.fchip}
                onClick={() => setBranch(b.id)}
              >
                {b.label}
              </button>
            ))}
          </div>
        </div>

        <div className={styles.chipBlock}>
          <span className={styles.toolLabel} id="rl-court">
            {C.rlCourt}
          </span>
          <div role="group" aria-labelledby="rl-court" className={styles.chipRowF}>
            {courts.map((c) => (
              <button
                key={c.id}
                type="button"
                aria-pressed={court === c.id}
                className={court === c.id ? styles.fchipOn : styles.fchip}
                onClick={() => {
                  setCourt(c.id);
                  setBench(null);
                }}
              >
                {c.label}
              </button>
            ))}
          </div>
        </div>

        {court === "bombay" && bombay.benches.length > 0 ? (
          <div className={styles.chipBlock}>
            <span className={styles.toolLabel} id="rl-bench">
              {C.rlBench}
            </span>
            <div role="group" aria-labelledby="rl-bench" className={styles.chipRowF}>
              <button
                type="button"
                aria-pressed={bench === null}
                className={bench === null ? styles.fchipOn : styles.fchip}
                onClick={() => setBench(null)}
              >
                {C.rlAllBenches}
              </button>
              {bombay.benches.map((b) => (
                <span key={b.code} className={styles.benchChipWrap}>
                  <BenchChip
                    code={b.code}
                    label={b.benchLabel}
                    count={b.count}
                    on={bench === b.code}
                    onClick={() => setBench(bench === b.code ? null : b.code)}
                  />
                </span>
              ))}
            </div>
          </div>
        ) : null}
      </div>

      {loading ? (
        <p className={styles.note} role="status">
          {C.rlLoading}
        </p>
      ) : null}

      {nothing ? (
        <EmptyState
          title={C.rlEmptyTitle}
          body={C.rlEmptyBody}
          action={filtersOn ? { label: C.rlClear, onClick: clearAll } : undefined}
        />
      ) : null}

      {background.length > 0 ? (
        <section className={styles.rlGroup} aria-labelledby="g-bg">
          <h2 id="g-bg" className={styles.rlGroupHead}>
            {C.rlBackgroundTitle}
          </h2>
          <p className={styles.groupMeta}>
            {reviewed ? `${C.rlLastReviewed(fmtDate(reviewed))}. ` : ""}
            {C.rlCurated}
          </p>
          <ul className={styles.rulings}>
            {background.map((e) => (
              <CuratedItem key={e.url} e={e} C={C} />
            ))}
          </ul>
        </section>
      ) : null}

      {featured.length > 0 ? (
        <section className={styles.rlGroup} aria-labelledby="g-ft">
          <h2 id="g-ft" className={styles.rlGroupHead}>
            {C.rlFeaturedTitle}
          </h2>
          <p className={styles.groupMeta}>
            {reviewed ? `${C.rlLastReviewed(fmtDate(reviewed))}. ` : ""}
            {C.rlCurated}
          </p>
          <ul className={styles.rulings}>
            {featured.map((e) => (
              <CuratedItem key={e.url} e={e} C={C} />
            ))}
          </ul>
        </section>
      ) : null}

      {(court === "all" || court === "sc") && archiveOn && (sc.rows.length > 0 || sc.status === "failed") ? (
        <section className={styles.rlGroup} aria-labelledby="g-sc">
          <h2 id="g-sc" className={styles.rlGroupHead}>
            {sc.meta?.groupLabel ?? C.cSupreme}
            <span className={styles.groupCourt}>{SC}</span>
          </h2>
          {sc.status === "failed" ? <p className={styles.flagNote}>{C.rlFailed}</p> : null}
          <ul className={styles.rulings}>
            {sc.rows.map((r) => (
              <ScItem key={r.link} r={r} C={C} />
            ))}
          </ul>
          {sc.hasMore ? (
            <div className={styles.moreRow}>
              <button type="button" className={styles.secondary} onClick={sc.loadMore} disabled={sc.status === "loading"}>
                {C.rlShowMore}
              </button>
              <span className={styles.count}>{C.rlShowing(sc.rows.length, sc.total)}</span>
            </div>
          ) : null}
          {archiveNotes(sc.meta, sc.meta?.count ? C.rlScSample(sc.meta.count) : null)}
        </section>
      ) : null}

      {(court === "all" || court === "bombay") && archiveOn && (bombay.rows.length > 0 || bombay.status === "failed") ? (
        <section className={styles.rlGroup} aria-labelledby="g-bb">
          <h2 id="g-bb" className={styles.rlGroupHead}>
            {bombay.meta?.groupLabel ?? C.cBombay}
            <span className={styles.groupCourt}>{BOMBAY}</span>
          </h2>
          {bombay.status === "failed" ? <p className={styles.flagNote}>{C.rlFailed}</p> : null}
          <ul className={styles.bombayList}>
            {bombay.rows.map((r) => (
              <BombayItem key={r.link} r={r} C={C} />
            ))}
          </ul>
          {bombay.hasMore ? (
            <div className={styles.moreRow}>
              <button
                type="button"
                className={styles.secondary}
                onClick={bombay.loadMore}
                disabled={bombay.status === "loading"}
              >
                {C.rlShowMore}
              </button>
              <span className={styles.count}>{C.rlShowing(bombay.rows.length, bombay.total)}</span>
            </div>
          ) : null}
          {archiveNotes(
            bombay.meta,
            bombay.meta?.sampleRule
              ? C.rlBombaySample(bombay.meta.sampleRule.perWeek, bombay.meta.sampleRule.weeks)
              : null,
          )}
        </section>
      ) : null}
    </>
  );
}

/** A bench filter chip. The tooltip shows on hover and on keyboard focus of the button itself. */
function BenchChip({
  code,
  label,
  count,
  on,
  onClick,
}: {
  code: string;
  label: string | null;
  count: number;
  on: boolean;
  onClick: () => void;
}) {
  const id = useId();
  const tip = useBenchTip(code, label);
  return (
    <span className={styles.tip}>
      <button
        type="button"
        aria-pressed={on}
        aria-describedby={id}
        className={on ? styles.fchipOn : styles.fchip}
        onClick={onClick}
      >
        {label ?? code}
        <span className={styles.chipCount}>{count}</span>
      </button>
      <span id={id} role="tooltip" className={styles.tipText}>
        {tip}
      </span>
    </span>
  );
}
