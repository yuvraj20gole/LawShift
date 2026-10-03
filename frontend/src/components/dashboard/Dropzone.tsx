"use client";

import { useRef, useState, type DragEvent } from "react";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { FlagIcon } from "@/components/auth/AuthParts";
import styles from "./dashboard.module.css";

const OK_TYPES = ["application/pdf", "image/jpeg", "image/png"];
const OK_EXT = /\.(pdf|jpe?g|png)$/i;

/**
 * Reusable upload control (PDF, JPG, PNG). UI only: it hands accepted files
 * to `onFiles` and shows a flag-styled message for anything else. Also used
 * in the workspace, where `compact` trims it down.
 */
export function Dropzone({
  onFiles,
  compact = false,
  id = "dropzone",
}: {
  onFiles: (files: File[]) => void;
  compact?: boolean;
  id?: string;
}) {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);
  const input = useRef<HTMLInputElement>(null);
  const [over, setOver] = useState(false);
  const [bad, setBad] = useState(false);

  function take(list: FileList | null) {
    if (!list || list.length === 0) return;
    const files = Array.from(list);
    const good = files.filter((f) => OK_TYPES.includes(f.type) || OK_EXT.test(f.name));
    setBad(good.length !== files.length);
    if (good.length) onFiles(good);
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
          <button type="button" className={styles.dzBtn} onClick={() => input.current?.click()}>
            {C.dzChoose}
          </button>
        </p>
        <p className={styles.dzTypes}>{C.dzTypes}</p>
        <input
          ref={input}
          id={id}
          type="file"
          accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
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
          {C.dzBad}
        </p>
      ) : null}
      <p className={styles.dzOcr}>{C.dzOcr}</p>
    </div>
  );
}
