"use client";

import { useEffect, useRef, useState } from "react";
import { usePrefs } from "@/lib/prefs";
import { getDocCopy } from "@/lib/documentsCopy";
import {
  attachCase,
  detachCase,
  docErrorMessage,
  extractDocument,
  listDocuments,
  markAttached,
  saveDocument,
  type DateSource,
  type Extraction,
  type ReadMethod,
  type StoredDoc,
} from "@/lib/documents";
import { isoToLong } from "@/lib/caseHistory";
import { Dropzone } from "./Dropzone";
import { DocumentReview, type ReviewResult } from "./DocumentReview";
import { FlagIcon } from "@/components/auth/AuthParts";
import styles from "./dashboard.module.css";
import docs from "./documents.module.css";

/** What the Workspace holds once a document is attached to this chat. */
export type Attachment = {
  name: string;
  iso: string;
  label: string;
  source: DateSource;
  readMethod: ReadMethod;
  description: string;
  saved: boolean;
};

type Source = "from" | "upload";
type Review =
  | { kind: "stored"; doc: StoredDoc }
  | { kind: "upload"; file: File; extraction: Extraction }
  | { kind: "change" };

/**
 * "Attach a document" above the chat. Nothing is attached until the user confirms the
 * offence date and presses a button; the conversation id is the one the chat uses.
 */
export function AttachDocument({
  conversationId,
  attachment,
  onAttach,
  onRemove,
}: {
  conversationId: string;
  attachment: Attachment | null;
  onAttach: (a: Attachment) => void;
  onRemove: () => void;
}) {
  const { lang } = usePrefs();
  const C = getDocCopy(lang);

  const [source, setSource] = useState<Source>("from");
  const [list, setList] = useState<StoredDoc[] | null>(null);
  const [listFailed, setListFailed] = useState(false);
  const [review, setReview] = useState<Review | null>(null);
  const [reading, setReading] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  /** A "Save and attach" that saved but failed to attach: do not save the file twice on retry. */
  const savedRow = useRef<StoredDoc | null>(null);
  const [preselect, setPreselect] = useState<string | null>(null);

  useEffect(() => {
    let id: string | null = null;
    try {
      id = sessionStorage.getItem("lawshift-doc");
      sessionStorage.removeItem("lawshift-doc");
    } catch {
      /* no preselected document */
    }
    // Strict Mode runs this twice; the second read finds the key cleared.
    if (id) setPreselect((prev) => prev ?? id);
  }, []);

  useEffect(() => {
    let live = true;
    listDocuments()
      .then((rows) => live && setList(rows))
      .catch(() => live && setListFailed(true));
    return () => {
      live = false;
    };
  }, []);

  useEffect(() => {
    if (!preselect || !list || attachment) return;
    const doc = list.find((x) => x.id === preselect);
    if (doc) {
      setSource("from");
      setReview({ kind: "stored", doc });
    }
    setPreselect(null);
  }, [preselect, list, attachment]);

  function reset() {
    setReview(null);
    setError(null);
    savedRow.current = null;
  }

  async function onFile(file: File) {
    setError(null);
    setReading(true);
    try {
      const extraction = await extractDocument(file);
      savedRow.current = null;
      setReview({ kind: "upload", file, extraction });
    } catch (e) {
      setError(docErrorMessage(e, C));
    } finally {
      setReading(false);
    }
  }

  async function onAction(id: string, r: ReviewResult) {
    if (!review) return;
    setBusyId(id);
    setError(null);
    try {
      let name = "";
      let saved = false;
      let readMethod: ReadMethod = "typed";
      let source: DateSource = r.source;
      if (review.kind === "stored") {
        name = review.doc.filename;
        saved = true;
        readMethod = review.doc.read_method;
        source = r.iso === review.doc.offence_date ? review.doc.date_source : "edited";
      } else if (review.kind === "upload") {
        name = review.file.name;
        readMethod = review.extraction.read_method;
        if (id === "save") {
          const row = savedRow.current ?? (await saveDocument(review.file, review.extraction, r.text, r.iso, r.source));
          savedRow.current = row;
          saved = true;
          setList((prev) => (prev ? [row, ...prev.filter((x) => x.id !== row.id)] : [row]));
        }
      } else if (attachment) {
        name = attachment.name;
        saved = attachment.saved;
        readMethod = attachment.readMethod;
        source = r.iso === attachment.iso ? attachment.source : "edited";
      }
      const res = await attachCase({
        conversation_id: conversationId,
        facts_text: r.text,
        offence_date: r.iso,
        date_source: source,
      });
      markAttached(conversationId);
      onAttach({
        name,
        iso: r.iso,
        label: res.offence_date_label || isoToLong(r.iso),
        source,
        readMethod,
        description: r.text,
        saved,
      });
      reset();
    } catch (e) {
      setError(docErrorMessage(e, C));
    } finally {
      setBusyId(null);
    }
  }

  async function remove() {
    setBusyId("remove");
    setError(null);
    try {
      await detachCase(conversationId);
      markAttached(null);
      onRemove();
    } catch (e) {
      setError(docErrorMessage(e, C));
    } finally {
      setBusyId(null);
    }
  }

  const readLabel = (m: ReadMethod) => (m === "ocr" ? C.readOcr : m === "docx" ? C.readDocx : C.readTyped);
  const errorLine = error ? (
    <p className={styles.flagNote} role="alert">
      <span className={styles.mark}>
        <FlagIcon />
      </span>
      {error}
    </p>
  ) : null;

  const reviewPanel =
    review?.kind === "stored" ? (
      <DocumentReview
        key={review.doc.id}
        filename={review.doc.filename}
        readMethod={review.doc.read_method}
        warnings={[]}
        showWarnings={false}
        candidates={[]}
        proposedIso={review.doc.date_source === "document" ? review.doc.offence_date : null}
        initialIso={review.doc.offence_date}
        documentText=""
        initialDescription={review.doc.extracted_text}
        actions={[{ id: "attach", label: C.wsAttachStored, primary: true }]}
        busyId={busyId}
        busyLabel={C.wsWorking}
        onAction={(id, r) => void onAction(id, r)}
        onCancel={reset}
        cancelLabel={C.wsCancel}
        error={error}
      />
    ) : review?.kind === "upload" ? (
      <DocumentReview
        filename={review.file.name}
        readMethod={review.extraction.read_method}
        warnings={review.extraction.warnings}
        candidates={review.extraction.date_candidates}
        proposedIso={review.extraction.date?.iso ?? null}
        initialIso={null}
        documentText={review.extraction.text}
        initialDescription=""
        actions={[
          { id: "chat", label: C.wsAttachOnly },
          { id: "save", label: C.wsSaveAttach, primary: true },
        ]}
        busyId={busyId}
        busyLabel={C.wsWorking}
        onAction={(id, r) => void onAction(id, r)}
        onCancel={reset}
        cancelLabel={C.wsCancel}
        error={error}
      />
    ) : review?.kind === "change" && attachment ? (
      <DocumentReview
        filename={attachment.name}
        readMethod={attachment.readMethod}
        warnings={[]}
        showWarnings={false}
        candidates={[]}
        proposedIso={attachment.source === "document" ? attachment.iso : null}
        initialIso={attachment.iso}
        documentText=""
        initialDescription={attachment.description}
        actions={[{ id: "change", label: C.wsAttachStored, primary: true }]}
        busyId={busyId}
        busyLabel={C.wsWorking}
        onAction={(id, r) => void onAction(id, r)}
        onCancel={reset}
        cancelLabel={C.wsCancel}
        error={error}
      />
    ) : null;

  return (
    <section className={styles.attach} aria-labelledby="attach-title">
      <h2 id="attach-title" className={styles.slotHead}>
        {C.wsAttachTitle}
      </h2>

      {attachment && !review ? (
        <div className={docs.chipWrap} key={attachment.name}>
          <p className={styles.chipRow}>
            <span className={styles.chip}>
              <span className={styles.chipTag}>{C.wsChip}</span>
              <strong className={docs.chipName}>{attachment.name}</strong>
            </span>
          </p>
          <p className={docs.chipMeta}>
            <span>{attachment.label}</span>
            <span>{readLabel(attachment.readMethod)}</span>
            <span>{attachment.saved ? C.wsSavedDoc : C.wsThisChatOnly}</span>
          </p>
          <p className={styles.chipRow}>
            <button type="button" className={docs.textBtn} onClick={() => setReview({ kind: "change" })}>
              {C.wsChangeDate}
            </button>
            <button type="button" className={styles.removeBtn} disabled={busyId === "remove"} onClick={() => void remove()}>
              {C.wsRemove}
              <span className="sr-only"> {attachment.name}</span>
            </button>
          </p>
          {errorLine}
          <p className={docs.after} role="status">
            {C.wsAfter}
          </p>
        </div>
      ) : review ? (
        reviewPanel
      ) : (
        <>
          <div role="radiogroup" aria-labelledby="attach-title" className={styles.segGroup}>
            <button
              type="button"
              role="radio"
              aria-checked={source === "from"}
              className={source === "from" ? styles.segOn : styles.seg}
              onClick={() => setSource("from")}
            >
              {C.wsFrom}
            </button>
            <button
              type="button"
              role="radio"
              aria-checked={source === "upload"}
              className={source === "upload" ? styles.segOn : styles.seg}
              onClick={() => setSource("upload")}
            >
              {C.wsUpload}
            </button>
          </div>

          {source === "from" ? (
            listFailed ? (
              <p className={styles.note}>{C.loadError}</p>
            ) : list === null ? (
              <p className={styles.note} role="status">
                {C.loading}
              </p>
            ) : list.length === 0 ? (
              <p className={styles.note}>{C.wsNone}</p>
            ) : (
              <fieldset className={styles.picker}>
                <legend className={styles.toolLabel}>{C.wsPick}</legend>
                {list.map((doc) => (
                  <label key={doc.id} className={styles.pickRow}>
                    <input
                      type="radio"
                      name="attach-doc"
                      onChange={() => {
                        setError(null);
                        setReview({ kind: "stored", doc });
                      }}
                    />
                    <span className={styles.pickName}>{doc.filename}</span>
                    <span className={styles.pickMeta}>
                      {isoToLong(doc.offence_date)} · {readLabel(doc.read_method)}
                    </span>
                  </label>
                ))}
              </fieldset>
            )
          ) : (
            <>
              <Dropzone compact id="attach-upload" onFile={(f) => void onFile(f)} disabled={reading} />
              {reading ? (
                <p className={docs.readingLine} role="status">
                  {C.reading}
                </p>
              ) : null}
            </>
          )}
          {errorLine}
        </>
      )}

    </section>
  );
}
