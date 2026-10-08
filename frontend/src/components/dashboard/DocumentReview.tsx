"use client";

import { useId, useMemo, useState } from "react";
import { usePrefs } from "@/lib/prefs";
import { getDocCopy } from "@/lib/documentsCopy";
import { FACTS_MAX_CHARS, FACTS_MIN_CHARS, type DateCandidate, type DateSource, type ReadMethod } from "@/lib/documents";
import { isoToLong } from "@/lib/caseHistory";
import { FlagIcon } from "@/components/auth/AuthParts";
import d from "./dashboard.module.css";
import styles from "./documents.module.css";

export type ReviewResult = { text: string; iso: string; source: DateSource };

export type ReviewAction = { id: string; label: string; primary?: boolean };

type Props = {
  filename: string;
  readMethod: ReadMethod;
  warnings: string[];
  candidates: DateCandidate[];
  /** The date the reader proposed. Keeping it records "document"; any other date records "edited". */
  proposedIso: string | null;
  /** The date selected when the panel opens (for example a stored or earlier-chosen date). */
  initialIso: string | null;
  /** The text read from the document: shown collapsed and read-only, never used as the query. Empty hides it. */
  documentText: string;
  /** Prefilled only for a saved document; empty for a fresh upload. */
  initialDescription: string;
  actions: ReviewAction[];
  /** Id of the action in flight (its button shows `busyLabel`), or null. */
  busyId: string | null;
  busyLabel: string;
  onAction: (id: string, result: ReviewResult) => void;
  onCancel: () => void;
  cancelLabel: string;
  error: string | null;
  /** Stored documents were already read: skip the warnings. */
  showWarnings?: boolean;
};

function validIso(s: string): boolean {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s);
  if (!m) return false;
  const dt = new Date(Date.UTC(+m[1], +m[2] - 1, +m[3]));
  return dt.getUTCFullYear() === +m[1] && dt.getUTCMonth() === +m[2] - 1 && dt.getUTCDate() === +m[3];
}

/**
 * The review step, used on the Documents page and in the Workspace: how the file was read,
 * what to watch for, the offence date (which the user must confirm), and the user's own
 * description of what happened (the search query).
 */
export function DocumentReview({
  filename,
  readMethod,
  warnings,
  candidates,
  proposedIso,
  initialIso,
  documentText,
  initialDescription,
  actions,
  busyId,
  busyLabel,
  onAction,
  onCancel,
  cancelLabel,
  error,
  showWarnings = true,
}: Props) {
  const { lang } = usePrefs();
  const C = getDocCopy(lang);
  const uid = useId();

  /** The candidates, plus the proposed date if it is not among them. */
  const options = useMemo(() => {
    const list = [...candidates];
    if (proposedIso && !list.some((c) => c.iso === proposedIso)) {
      list.unshift({ iso: proposedIso, label: isoToLong(proposedIso), context: "" });
    }
    return list;
  }, [candidates, proposedIso]);

  const startIso = initialIso ?? proposedIso ?? "";
  const startsOnOption = options.some((o) => o.iso === startIso);
  const [choice, setChoice] = useState<string>(startsOnOption ? startIso : "manual");
  const [manual, setManual] = useState<string>(startsOnOption ? "" : startIso);
  const [confirmed, setConfirmed] = useState(false);
  const [text, setText] = useState(initialDescription.slice(0, FACTS_MAX_CHARS));

  const iso = choice === "manual" ? manual : choice;
  const isoOk = validIso(iso);
  const source: DateSource = proposedIso !== null && iso === proposedIso ? "document" : "edited";
  const factsOk = text.trim().length >= FACTS_MIN_CHARS;
  const ready = isoOk && confirmed && factsOk && busyId === null;
  const busy = busyId !== null;

  function pick(next: string) {
    setChoice(next);
    setConfirmed(false);
  }

  const readLabel = readMethod === "ocr" ? C.readOcr : readMethod === "docx" ? C.readDocx : C.readTyped;
  const warnText: Record<string, string> = {
    ocr_may_misread_digits: C.wOcr,
    no_text_found: C.wNoText,
    truncated: C.wTruncated,
    multiple_dates: C.wMultiple,
    pages_skipped: C.wPages,
    password_protected: C.wPassword,
  };
  const shown = showWarnings ? warnings.filter((w) => warnText[w]) : [];

  return (
    <section className={styles.review} aria-labelledby={`${uid}-t`}>
      <h3 id={`${uid}-t`} className={styles.reviewTitle}>
        {C.rvTitle}
      </h3>

      <dl className={styles.facts}>
        <div>
          <dt>{C.rvFile}</dt>
          <dd className={styles.fname}>{filename}</dd>
        </div>
        <div>
          <dt>{C.rvHow}</dt>
          <dd>{readLabel}</dd>
        </div>
      </dl>

      {shown.length > 0 ? (
        <ul className={styles.warns}>
          {shown.map((w) => (
            <li key={w} className={d.flagNote}>
              <span className={d.mark}>
                <FlagIcon />
              </span>
              {warnText[w]}
            </li>
          ))}
        </ul>
      ) : null}

      <fieldset className={styles.dateSet}>
        <legend className={d.toolLabel}>{C.dateTitle}</legend>
        {options.length === 0 ? <p className={d.note}>{C.dateNone}</p> : null}
        <div className={styles.opts}>
          {options.map((o) => (
            <label key={o.iso} className={styles.opt}>
              <input
                type="radio"
                name={`${uid}-date`}
                checked={choice === o.iso}
                onChange={() => pick(o.iso)}
                disabled={busy}
              />
              <span>
                <strong>{o.label || isoToLong(o.iso)}</strong>
                {o.context ? <span className={styles.ctx}>{o.context}</span> : null}
              </span>
            </label>
          ))}
          <label className={styles.opt}>
            <input
              type="radio"
              name={`${uid}-date`}
              checked={choice === "manual"}
              onChange={() => pick("manual")}
              disabled={busy}
            />
            <span>
              <strong>{C.dateManualOption}</strong>
            </span>
          </label>
        </div>
        {choice === "manual" ? (
          <div className={styles.manual}>
            <label htmlFor={`${uid}-manual`} className={d.toolLabel}>
              {C.dateInputLabel}
            </label>
            <input
              id={`${uid}-manual`}
              type="date"
              className={d.searchInput}
              value={manual}
              onChange={(e) => {
                setManual(e.target.value);
                setConfirmed(false);
              }}
              disabled={busy}
            />
          </div>
        ) : null}
        {isoOk && source === "edited" ? <p className={d.note}>{C.dateEditedNote}</p> : null}
        <label className={styles.confirmBox}>
          <input
            type="checkbox"
            checked={confirmed}
            disabled={!isoOk || busy}
            onChange={(e) => setConfirmed(e.target.checked)}
          />
          <span>{C.dateConfirm}</span>
        </label>
      </fieldset>

      <div className={styles.factsBlock}>
        <label htmlFor={`${uid}-facts`} className={d.toolLabel}>
          {C.descTitle}
        </label>
        <p className={d.note} id={`${uid}-help`}>
          {C.descHelp}
        </p>
        <textarea
          id={`${uid}-facts`}
          className={styles.factsBox}
          rows={5}
          maxLength={FACTS_MAX_CHARS}
          value={text}
          aria-describedby={`${uid}-help`}
          onChange={(e) => setText(e.target.value)}
          disabled={busy}
        />
        <p className={styles.counter} aria-live="polite">
          {C.descCount(text.length, FACTS_MAX_CHARS)}
        </p>
      </div>

      {documentText ? (
        <details className={styles.readText}>
          <summary>{C.textReadTitle}</summary>
          <p className={d.note}>{C.textReadNote}</p>
          <textarea className={styles.readBox} readOnly rows={8} value={documentText} aria-label={C.textReadTitle} />
        </details>
      ) : null}

      {error ? (
        <p className={d.flagNote} role="alert">
          <span className={d.mark}>
            <FlagIcon />
          </span>
          {error}
        </p>
      ) : null}

      <div className={styles.actions}>
        {actions.map((a) => (
          <button
            key={a.id}
            type="button"
            className={a.primary ? d.primary : d.secondary}
            disabled={!ready}
            onClick={() => onAction(a.id, { text: text.trim(), iso, source })}
          >
            {busyId === a.id ? busyLabel : a.label}
          </button>
        ))}
        <button type="button" className={styles.cancelBtn} onClick={onCancel} disabled={busy}>
          {cancelLabel}
        </button>
      </div>
      {!ready && !busy ? (
        <p className={d.note}>{!isoOk || !confirmed ? C.needConfirm : !factsOk ? C.descShort : ""}</p>
      ) : null}
    </section>
  );
}
