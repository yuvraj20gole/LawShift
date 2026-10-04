"use client";

import { useEffect, useId, useMemo, useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import Link from "next/link";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { API_BASE } from "@/lib/api";
import { diffWords, plain, type Seg } from "@/lib/wordDiff";
import { CodeCompare, type CardData } from "@/components/CodeCompare";
import { PageHead } from "@/components/dashboard/DashParts";
import styles from "@/components/dashboard/dashboard.module.css";

type Code = "IPC" | "BNS";
type Suggest = { section: string; title: string };
type IpcCard = { code: "IPC"; section: string; heading: string; text: string };
type BnsCard = { code: "BNS"; section: string; base?: string; heading: string; text: string };
type Pair = {
  mappingType: "section" | "partial" | "merged" | "dropped";
  ipc: IpcCard;
  bns: BnsCard | null;
  datasetEntry: string | null;
};
type Result = {
  code: Code;
  section: string;
  found: boolean;
  title: string;
  pairs: Pair[];
  bnsOnly?: { section: string; heading: string; text: string };
};

export default function MappingPage() {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);
  const listId = useId();

  const [code, setCode] = useState<Code>("IPC");
  const [text, setText] = useState("");
  const [lists, setLists] = useState<Partial<Record<Code, Suggest[]>>>({});
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Section numbers and titles for the suggestions: one small request per code.
  useEffect(() => {
    if (lists[code]) return;
    let alive = true;
    fetch(`${API_BASE}/api/map/sections?code=${code}`)
      .then((r) => r.json())
      .then((d) => alive && setLists((l) => ({ ...l, [code]: d.sections ?? [] })))
      .catch(() => undefined);
    return () => {
      alive = false;
    };
  }, [code, lists]);

  const suggestions = useMemo(() => {
    const q = text.trim().toLowerCase();
    const all = lists[code] ?? [];
    if (!q) return [];
    const byNumber = /^\d/.test(q);
    return all
      .filter((s) => (byNumber ? s.section.toLowerCase().startsWith(q) : s.title.toLowerCase().includes(q)))
      .slice(0, 8);
  }, [text, lists, code]);

  async function lookup(section: string) {
    const s = section.trim();
    if (!s) return;
    setOpen(false);
    setBusy(true);
    setFailed(false);
    try {
      const r = await fetch(`${API_BASE}/api/map?code=${code}&section=${encodeURIComponent(s)}`);
      if (!r.ok) throw new Error(String(r.status));
      setResult((await r.json()) as Result);
    } catch {
      setFailed(true);
      setResult(null);
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    const pick = active >= 0 ? suggestions[active] : null;
    if (pick) setText(pick.section);
    void lookup(pick ? pick.section : text);
  }

  function onKey(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setOpen(true);
      setActive((a) => Math.min(suggestions.length - 1, a + 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((a) => Math.max(-1, a - 1));
    } else if (e.key === "Escape") {
      setOpen(false);
      setActive(-1);
    }
  }

  function switchCode(c: Code) {
    setCode(c);
    setText("");
    setResult(null);
    setFailed(false);
    setActive(-1);
  }

  // ---- result -> cards -------------------------------------------------
  const view = useMemo(() => {
    if (!result || !result.found) return null;
    const left: CardData[] = [];
    const right: CardData[] = [];
    const seenL = new Set<string>();
    const seenR = new Set<string>();

    for (const p of result.pairs) {
      const d = p.bns ? diffWords(p.ipc.text, p.bns.text) : null;
      if (!seenL.has(p.ipc.section)) {
        seenL.add(p.ipc.section);
        left.push({
          id: `ipc-${p.ipc.section}`,
          code: "IPC",
          title: `IPC ${p.ipc.section}`,
          heading: p.ipc.heading,
          span: C.mapIpcSpan,
          rows: [{ segs: d ? d.a : plain(p.ipc.text), scroll: true }],
        });
      }
      if (p.bns && !seenR.has(p.bns.section)) {
        seenR.add(p.bns.section);
        right.push({
          id: `bns-${p.bns.section}`,
          code: "BNS",
          title: `BNS ${p.bns.section}`,
          heading: p.bns.heading,
          span: C.mapBnsSpan,
          rows: [{ segs: d ? d.b : plain(p.bns.text), scroll: true }],
        });
      }
    }
    if (result.bnsOnly && !right.length) {
      right.push({
        id: `bns-${result.bnsOnly.section}`,
        code: "BNS",
        title: `BNS ${result.bnsOnly.section}`,
        heading: result.bnsOnly.heading,
        span: C.mapBnsSpan,
        rows: [{ segs: plain(result.bnsOnly.text), scroll: true }],
      });
    }
    return { left, right };
  }, [result, C]);

  const typeLine = (p: Pair) =>
    p.mappingType === "section"
      ? C.mapTypeSection
      : p.mappingType === "partial"
        ? C.mapTypePartial(p.bns?.section ?? "")
        : p.mappingType === "merged"
          ? C.mapTypeMerged
          : C.mapTypeDropped;

  const noEquivBox = (entry?: string | null, bnsOnly?: boolean) => (
    <div className={styles.noEquiv} role="status">
      <p className={styles.noEquivTitle}>{C.mapNoEquiv}</p>
      {bnsOnly ? <p className={styles.note}>{C.mapBnsOnly}</p> : null}
      {entry ? <p className={styles.note}>{C.mapEntry(entry)}</p> : null}
    </div>
  );

  function carry() {
    if (!result) return;
    const ipc = result.pairs[0]?.ipc.section;
    const bns = result.pairs[0]?.bns?.section;
    const subject =
      result.code === "IPC"
        ? `IPC ${result.section}${bns ? ` (BNS ${bns} in the mapping table)` : ""}`
        : `BNS ${result.section}${ipc ? ` (IPC ${ipc} in the mapping table)` : ""}`;
    try {
      sessionStorage.setItem("lawshift-carry", `I am looking at ${subject}. The offence happened on `);
    } catch {
      /* ignore */
    }
  }

  const types = result?.pairs.length ? result.pairs : [];

  return (
    <>
      <PageHead title={C.mapTitle} lede={C.mapLede} />

      <form className={styles.lookup} onSubmit={onSubmit} role="search">
        <div className={styles.stepBlock}>
          <span className={styles.toolLabel} id="map-code-label">
            {C.mapStepCode}
          </span>
          <div role="radiogroup" aria-labelledby="map-code-label" className={styles.segGroup}>
            {(["IPC", "BNS"] as Code[]).map((c) => (
              <button
                key={c}
                type="button"
                role="radio"
                aria-checked={code === c}
                className={code === c ? styles.segOn : styles.seg}
                onClick={() => switchCode(c)}
              >
                {c === "IPC" ? C.mapFromIpc : C.mapFromBns}
              </button>
            ))}
          </div>
        </div>

        <div className={styles.stepBlock}>
          <label htmlFor="map-section" className={styles.toolLabel}>
            {C.mapSectionLabel}
          </label>
          <div className={styles.combo}>
            <input
              id="map-section"
              ref={inputRef}
              className={styles.searchInput}
              value={text}
              placeholder={C.mapSectionHint}
              autoComplete="off"
              spellCheck={false}
              role="combobox"
              aria-expanded={open && suggestions.length > 0}
              aria-controls={listId}
              aria-autocomplete="list"
              aria-activedescendant={active >= 0 ? `${listId}-${active}` : undefined}
              onChange={(e) => {
                setText(e.target.value);
                setOpen(true);
                setActive(-1);
              }}
              onFocus={() => setOpen(true)}
              onBlur={() => setTimeout(() => setOpen(false), 120)}
              onKeyDown={onKey}
            />
            {open && suggestions.length > 0 ? (
              <ul id={listId} role="listbox" aria-label={C.mapSuggestions} className={styles.suggest}>
                {suggestions.map((s, i) => (
                  <li
                    key={s.section}
                    id={`${listId}-${i}`}
                    role="option"
                    aria-selected={i === active}
                    className={i === active ? styles.sugOn : styles.sug}
                    onMouseDown={(e) => {
                      e.preventDefault();
                      setText(s.section);
                      void lookup(s.section);
                    }}
                  >
                    <strong>{s.section}</strong>
                    <span>{s.title}</span>
                  </li>
                ))}
              </ul>
            ) : null}
          </div>
        </div>

        <button type="submit" className={styles.primary} disabled={busy || text.trim() === ""}>
          {busy ? C.mapLooking : C.mapLookup}
        </button>
      </form>

      {failed ? (
        <p className={styles.flagNote} role="alert">
          {C.mapOffline}
        </p>
      ) : null}

      {result && !result.found ? (
        <p className={styles.flagNote} role="alert">
          {C.mapNotFound(result.code, result.section)}
        </p>
      ) : null}

      {result && result.found && view ? (
        <section className={styles.mapResult} aria-live="polite" aria-label={C.mapResultFor(result.code, result.section)}>
          <h2 className={styles.mapResultHead}>{C.mapResultFor(result.code, result.section)}</h2>
          {result.title ? <p className={styles.mapResultSub}>{result.title}</p> : null}

          {types.length > 0 ? (
            <div className={styles.typeBlock}>
              <p className={styles.toolLabel}>{C.mapTypeLabel}</p>
              <ul className={styles.typeList}>
                {types.map((p, i) => (
                  <li key={i}>
                    {types.length > 1 ? (
                      <strong>
                        IPC {p.ipc.section}
                        {p.bns ? ` → BNS ${p.bns.section}` : ""}:{" "}
                      </strong>
                    ) : null}
                    {typeLine(p)}
                  </li>
                ))}
              </ul>
              {result.code === "BNS" && result.pairs.length > 1 ? <p className={styles.note}>{C.mapManyIpc}</p> : null}
            </div>
          ) : null}

          <CodeCompare
            left={view.left}
            right={view.right}
            swapLabel={C.mapSwap}
            leftEmpty={noEquivBox(null, true)}
            rightEmpty={noEquivBox(result.pairs[0]?.datasetEntry, false)}
          />

          {view.left.length > 0 && view.right.length > 0 ? <p className={styles.note}>{C.mapDiffNote}</p> : null}

          <div className={styles.mapNote}>
            <p>{C.mapNote}</p>
            <Link href="/dashboard/workspace" className={styles.primary} onClick={carry}>
              {C.mapAsk}
            </Link>
            <p className={styles.note}>{C.mapCaveat}</p>
          </div>
        </section>
      ) : null}
    </>
  );
}
