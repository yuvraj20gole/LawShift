"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { usePrefs } from "@/lib/prefs";
import { getDocCopy } from "@/lib/documentsCopy";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import {
  deleteAllDocuments,
  deleteDocument,
  docErrorMessage,
  extractDocument,
  formatSize,
  listDocuments,
  saveDocument,
  signedUrl,
  type Extraction,
  type StoredDoc,
} from "@/lib/documents";
import { isoToLong } from "@/lib/caseHistory";
import { Dropzone } from "@/components/dashboard/Dropzone";
import { DocumentReview, type ReviewResult } from "@/components/dashboard/DocumentReview";
import { EmptyState, PageHead } from "@/components/dashboard/DashParts";
import { CheckIcon, FlagIcon } from "@/components/auth/AuthParts";
import styles from "@/components/dashboard/dashboard.module.css";
import docs from "@/components/dashboard/documents.module.css";

type Load = "loading" | "error" | "ready";
type Pending = { file: File; extraction: Extraction };

export default function DocumentsPage() {
  const { lang } = usePrefs();
  const router = useRouter();
  const C = getDocCopy(lang);
  const D = getDashboardCopy(lang);

  const [load, setLoad] = useState<Load>("loading");
  const [items, setItems] = useState<StoredDoc[]>([]);
  const [reading, setReading] = useState(false);
  const [pending, setPending] = useState<Pending | null>(null);
  const [saving, setSaving] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [justSaved, setJustSaved] = useState(false);
  const [confirmId, setConfirmId] = useState<string | null>(null);
  const [confirmAll, setConfirmAll] = useState(false);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const fetchDocs = useCallback(async () => {
    setLoad("loading");
    try {
      setItems(await listDocuments());
      setLoad("ready");
    } catch {
      setLoad("error");
    }
  }, []);

  useEffect(() => {
    void fetchDocs();
  }, [fetchDocs]);

  async function onFile(file: File) {
    setUploadError(null);
    setJustSaved(false);
    setPending(null);
    setReading(true);
    try {
      setPending({ file, extraction: await extractDocument(file) });
    } catch (e) {
      setUploadError(docErrorMessage(e, C));
    } finally {
      setReading(false);
    }
  }

  async function onSave(_id: string, r: ReviewResult) {
    if (!pending) return;
    setSaving(true);
    setUploadError(null);
    try {
      const row = await saveDocument(pending.file, pending.extraction, r.text, r.iso, r.source);
      setItems((prev) => [row, ...prev]);
      setPending(null);
      setJustSaved(true);
      if (load !== "ready") setLoad("ready");
    } catch (e) {
      setUploadError(docErrorMessage(e, C));
    } finally {
      setSaving(false);
    }
  }

  async function onDelete(doc: StoredDoc) {
    setBusyId(doc.id);
    setActionError(null);
    try {
      await deleteDocument(doc);
      setItems((prev) => prev.filter((x) => x.id !== doc.id));
      setConfirmId(null);
    } catch (e) {
      setActionError(docErrorMessage(e, C));
    } finally {
      setBusyId(null);
    }
  }

  async function onDeleteAll() {
    setBusyId("all");
    setActionError(null);
    try {
      await deleteAllDocuments(items);
      setItems([]);
      setConfirmAll(false);
    } catch (e) {
      setActionError(docErrorMessage(e, C));
      void fetchDocs();
    } finally {
      setBusyId(null);
    }
  }

  async function onDownload(doc: StoredDoc) {
    setBusyId(doc.id);
    setActionError(null);
    try {
      window.location.assign(await signedUrl(doc.storage_path, doc.filename));
    } catch (e) {
      setActionError(docErrorMessage(e, C));
    } finally {
      setBusyId(null);
    }
  }

  function openInWorkspace(doc: StoredDoc) {
    try {
      sessionStorage.setItem("lawshift-doc", doc.id);
    } catch {
      /* the Workspace opens without a preselected document */
    }
    router.push("/dashboard/workspace");
  }

  const readLabel = (m: StoredDoc["read_method"]) =>
    m === "ocr" ? C.readOcr : m === "docx" ? C.readDocx : C.readTyped;
  const savedOn = (iso: string) => {
    const dt = new Date(iso);
    return Number.isNaN(dt.getTime()) ? "" : isoToLong(dt.toISOString().slice(0, 10));
  };

  return (
    <>
      <PageHead title={D.dcTitle} lede={C.dcLede} />
      <p className={docs.store}>{C.dcStoreNote}</p>

      <h2 className={styles.listHead}>{C.dcUploadTitle}</h2>
      {pending ? null : <Dropzone onFile={(f) => void onFile(f)} disabled={reading || saving} />}
      {reading ? (
        <p className={docs.readingLine} role="status">
          {C.reading}
        </p>
      ) : null}
      {uploadError && !pending ? (
        <p className={`${styles.flagNote} ${docs.errLine}`} role="alert">
          <span className={styles.mark}>
            <FlagIcon />
          </span>
          {uploadError}
        </p>
      ) : null}
      {justSaved && !pending ? (
        <p className={docs.savedLine} role="status">
          <CheckIcon />
          {C.saved}
        </p>
      ) : null}
      {pending ? (
        <DocumentReview
          filename={pending.file.name}
          readMethod={pending.extraction.read_method}
          warnings={pending.extraction.warnings}
          candidates={pending.extraction.date_candidates}
          proposedIso={pending.extraction.date?.iso ?? null}
          initialIso={null}
          documentText={pending.extraction.text}
          initialDescription=""
          actions={[{ id: "save", label: C.save, primary: true }]}
          busyId={saving ? "save" : null}
          busyLabel={C.saving}
          onAction={(id, r) => void onSave(id, r)}
          onCancel={() => {
            setPending(null);
            setUploadError(null);
          }}
          cancelLabel={C.discard}
          error={uploadError}
        />
      ) : null}

      <div className={docs.listBar}>
        <h2 className={styles.listHead}>{C.dcListTitle}</h2>
      </div>

      {actionError ? (
        <p className={`${styles.flagNote} ${docs.errLine}`} role="alert">
          <span className={styles.mark}>
            <FlagIcon />
          </span>
          {actionError}
        </p>
      ) : null}

      {load === "loading" ? (
        <p className={styles.loadingLine} role="status">
          {C.loading}
        </p>
      ) : load === "error" ? (
        <EmptyState title={C.loadError} body="" action={{ label: C.retry, onClick: () => void fetchDocs() }} />
      ) : items.length === 0 ? (
        <EmptyState title={C.emptyTitle} body={C.emptyBody} />
      ) : (
        <>
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th scope="col">{C.colFile}</th>
                  <th scope="col">{C.colSaved}</th>
                  <th scope="col">{C.colRead}</th>
                  <th scope="col">{C.colDate}</th>
                  <th scope="col">{C.colSize}</th>
                  <th scope="col">{C.colActions}</th>
                </tr>
              </thead>
              <tbody>
                {items.map((doc, i) => (
                  <tr key={doc.id} style={{ ["--i" as string]: i }}>
                    <td data-label={C.colFile}>
                      <strong className={docs.docName}>{doc.filename}</strong>
                    </td>
                    <td data-label={C.colSaved}>{savedOn(doc.created_at)}</td>
                    <td data-label={C.colRead}>
                      <span className={doc.read_method === "ocr" ? styles.readOcr : styles.readPlain}>
                        {readLabel(doc.read_method)}
                      </span>
                    </td>
                    <td data-label={C.colDate}>{isoToLong(doc.offence_date)}</td>
                    <td data-label={C.colSize}>{formatSize(doc.size_bytes)}</td>
                    <td data-label={C.colActions}>
                      {confirmId === doc.id ? (
                        <div className={styles.confirm} role="alertdialog" aria-labelledby={`del-${doc.id}`}>
                          <p id={`del-${doc.id}`} className={styles.confirmTitle}>
                            <FlagIcon />
                            {C.delTitle}
                          </p>
                          <p className={styles.confirmBody}>{C.delBody}</p>
                          <div className={styles.confirmActions}>
                            <button
                              type="button"
                              className={styles.dangerBtn}
                              disabled={busyId === doc.id}
                              onClick={() => void onDelete(doc)}
                            >
                              {C.delConfirm}
                            </button>
                            <button type="button" className={styles.secondary} onClick={() => setConfirmId(null)}>
                              {C.cancel}
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className={docs.docActions}>
                          <button type="button" onClick={() => openInWorkspace(doc)}>
                            {C.useInWorkspace}
                            <span className="sr-only"> {doc.filename}</span>
                          </button>
                          <button type="button" disabled={busyId === doc.id} onClick={() => void onDownload(doc)}>
                            {C.download}
                            <span className="sr-only"> {doc.filename}</span>
                          </button>
                          <button
                            type="button"
                            className={docs.del}
                            onClick={() => {
                              setConfirmId(doc.id);
                              setConfirmAll(false);
                            }}
                          >
                            {C.del}
                            <span className="sr-only"> {doc.filename}</span>
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className={styles.clearRow}>
            {confirmAll ? (
              <div className={styles.confirm} role="alertdialog" aria-labelledby="delall-title">
                <p id="delall-title" className={styles.confirmTitle}>
                  <FlagIcon />
                  {C.delAllTitle(items.length)}
                </p>
                <p className={styles.confirmBody}>{C.delAllBody}</p>
                <div className={styles.confirmActions}>
                  <button
                    type="button"
                    className={styles.dangerBtn}
                    disabled={busyId === "all"}
                    onClick={() => void onDeleteAll()}
                  >
                    {C.delAllConfirm}
                  </button>
                  <button type="button" className={styles.secondary} onClick={() => setConfirmAll(false)}>
                    {C.cancel}
                  </button>
                </div>
              </div>
            ) : (
              <button
                type="button"
                className={styles.rowDelete}
                onClick={() => {
                  setConfirmAll(true);
                  setConfirmId(null);
                }}
              >
                {C.delAll}
              </button>
            )}
          </div>
        </>
      )}
    </>
  );
}
