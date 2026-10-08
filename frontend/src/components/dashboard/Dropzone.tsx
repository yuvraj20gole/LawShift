"use client";

import { useRef, useState, type DragEvent } from "react";
import { usePrefs } from "@/lib/prefs";
import { getDocCopy } from "@/lib/documentsCopy";
import { DocError, checkFile, docErrorMessage } from "@/lib/documents";
import { FlagIcon } from "@/components/auth/AuthParts";
import styles from "./dashboard.module.css";

/**
 * Upload control for one file (PDF, JPG, PNG or DOCX, up to 10 MB). It checks the type and
 * size, then hands the file to `onFile`; anything else gets a flag-styled message.
 */
export function Dropzone({
  onFile,
  compact = false,
  id = "dropzone",
  disabled = false,
}: {
  onFile: (file: File) => void;
  compact?: boolean;
  id?: string;
  disabled?: boolean;
}) {
  const { lang } = usePrefs();
  const C = getDocCopy(lang);
  const input = useRef<HTMLInputElement>(null);
  const [over, setOver] = useState(false);
  const [bad, setBad] = useState<string | null>(null);

  function take(list: FileList | null) {
    if (disabled || !list || list.length === 0) return;
    const f = list[0];
    const problem = checkFile(f);
    if (problem) {
      setBad(docErrorMessage(new DocError(problem), C));
      return;
    }
    setBad(null);
    onFile(f);
  }

  function onDrop(e: DragEvent) {
    e.preventDefault();
    setOver(false);
    take(e.dataTransfer.files);
  }

  return (
    <div className={compact ? styles.dzCompact : undefined}>
      <div
        className={`${styles.dz} ${over ? styles.dzOver : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setOver(true);
        }}
        onDragLeave={() => setOver(false)}
        onDrop={onDrop}
      >
        <p className={styles.dzLine}>
          {C.dzTitle}{" "}
          <button type="button" className={styles.dzBtn} disabled={disabled} onClick={() => input.current?.click()}>
            {C.dzChoose}
          </button>
        </p>
        <p className={styles.dzTypes}>{C.dzTypes}</p>
        <input
          ref={input}
          id={id}
          type="file"
          accept=".pdf,.jpg,.jpeg,.png,.docx,application/pdf,image/jpeg,image/png,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          className="sr-only"
          tabIndex={-1}
          aria-label={C.dzChoose}
          onChange={(e) => {
            take(e.target.files);
            e.target.value = "";
          }}
        />
      </div>
      {bad ? (
        <p className={styles.flagNote} role="alert">
          <span className={styles.mark}>
            <FlagIcon />
          </span>
          {bad}
        </p>
      ) : null}
    </div>
  );
}
