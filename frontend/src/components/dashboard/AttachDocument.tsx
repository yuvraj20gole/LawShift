"use client";

import { useState } from "react";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { SAMPLE_DOCS, type SampleDoc } from "@/lib/sampleData";
import { Dropzone } from "./Dropzone";
import { usePreviewMode } from "./DashboardShell";
import { CheckIcon } from "@/components/auth/AuthParts";
import styles from "./dashboard.module.css";

type Source = "from" | "upload";
type DateState = "found" | "editing" | "confirmed";

type Attached = { name: string; read: SampleDoc["read"]; date: string };

/**
 * "Attach a document" above the chat. The document supplies the facts and
 * the offence date for the conversation; the date must be confirmed or
 * edited before it locks. UI only: nothing here changes what the chat sends.
 */
export function AttachDocument() {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);
  const mode = usePreviewMode();
  const docs = mode === "empty" ? [] : SAMPLE_DOCS;

  const [source, setSource] = useState<Source>("from");
  const [attached, setAttached] = useState<Attached | null>(null);
  const [dateState, setDateState] = useState<DateState>("found");
  const [draft, setDraft] = useState("");

  function attachSample(id: string) {
    const d = docs.find((x) => x.id === id);
    if (!d) return;
    setAttached({ name: d.name, read: d.read, date: d.foundDate ?? "" });
    setDraft(d.foundDate ?? "");
    setDateState(d.foundDate ? "found" : "editing");
  }

  function attachUpload(files: File[]) {
    const f = files[0];
    if (!f) return;
    // The preview does not read files, so no date is "found": the user enters it.
    setAttached({ name: f.name, read: "pending", date: "" });
    setDraft("");
    setDateState("editing");
  }

  function clear() {
    setAttached(null);
    setDraft("");
    setDateState("found");
  }

  const date = attached?.date ?? "";

  return (
    <section className={styles.attach} aria-labelledby="attach-title">
      <h2 id="attach-title" className={styles.slotHead}>
        {C.atTitle}
      </h2>

      {!attached ? (
        <>
          <div role="radiogroup" aria-labelledby="attach-title" className={styles.segGroup}>
            <button
              type="button"
              role="radio"
              aria-checked={source === "from"}
              className={source === "from" ? styles.segOn : styles.seg}
              onClick={() => setSource("from")}
            >
              {C.atFrom}
            </button>
            <button
              type="button"
              role="radio"
              aria-checked={source === "upload"}
              className={source === "upload" ? styles.segOn : styles.seg}
              onClick={() => setSource("upload")}
            >
              {C.atUpload}
            </button>
          </div>

          {source === "from" ? (
            docs.length === 0 ? (
              <p className={styles.note}>{C.atNoDocs}</p>
            ) : (
              <fieldset className={styles.picker}>
                <legend className={styles.toolLabel}>{C.atPickLabel}</legend>
                {docs.map((d) => (
                  <label key={d.id} className={styles.pickRow}>
                    <input type="radio" name="attach-doc" onChange={() => attachSample(d.id)} />
                    <span className={styles.pickName}>{d.name}</span>
                    <span className={styles.pickMeta}>
                      {d.date} · {d.read === "direct" ? C.readDirect : d.read === "ocr" ? C.readOcr : C.readPending}
                    </span>
                  </label>
                ))}
              </fieldset>
            )
          ) : (
            <Dropzone compact acceptWord id="attach-upload" onFiles={attachUpload} />
          )}
        </>
      ) : (
        <div className={styles.attached} key={attached.name}>
          <p className={styles.chipRow}>
            <span className={styles.chip}>
              <span className={styles.chipTag}>{C.atChip}</span>
              <strong>{attached.name}</strong>
            </span>
            <button type="button" className={styles.removeBtn} onClick={clear}>
              {C.atRemove}
              <span className="sr-only"> {attached.name}</span>
            </button>
          </p>

          {dateState === "editing" ? (
            <div className={styles.dateEdit}>
              <label htmlFor="attach-date" className={styles.toolLabel}>
                {C.atDateLabel}
              </label>
              <div className={styles.dateRow}>
                <input
                  id="attach-date"
                  className={styles.searchInput}
                  value={draft}
                  placeholder="5 September 2024"
                  onChange={(e) => setDraft(e.target.value)}
                  autoComplete="off"
                />
                <button
                  type="button"
                  className={styles.secondary}
                  disabled={draft.trim() === ""}
                  onClick={() => {
                    setAttached((a) => (a ? { ...a, date: draft.trim() } : a));
                    setDateState("found");
                  }}
                >
                  {C.atSave}
                </button>
              </div>
            </div>
          ) : dateState === "confirmed" ? (
            <p className={styles.stateOk} role="status">
              <CheckIcon />
              {C.atConfirmed(date)}{" "}
              <button type="button" className={styles.inlineLink} onClick={() => setDateState("editing")}>
                {C.atChange}
              </button>
            </p>
          ) : (
            <div className={styles.dateFound}>
              <p className={styles.dateLine}>
                {date ? C.atDateFound(date) : C.atDateNone}{" "}
                <button type="button" className={styles.inlineLink} onClick={() => setDateState("editing")}>
                  {C.atEdit}
                </button>
              </p>
              {date ? (
                <button type="button" className={styles.primary} onClick={() => setDateState("confirmed")}>
                  {C.atConfirm}
                </button>
              ) : null}
            </div>
          )}

          <p className={styles.note}>{C.atScanNote}</p>
        </div>
      )}

      <p className={styles.note}>{C.atPreview}</p>
    </section>
  );
}
