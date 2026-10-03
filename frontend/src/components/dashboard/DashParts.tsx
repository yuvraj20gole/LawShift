"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import styles from "./dashboard.module.css";
import { CheckIcon, FlagIcon } from "@/components/auth/AuthParts";
import type { Code } from "@/lib/sampleData";

/** IPC slate / BNS navy: the same two code colours as the landing page. */
export function CodeBadge({ code }: { code: Code }) {
  return <span className={code === "IPC" ? styles.badgeIpc : styles.badgeBns}>{code}</span>;
}

/** Verification state is always an icon plus words, never colour alone. */
export function VerifyState({ flagged, okText, flagText }: { flagged: boolean; okText: string; flagText: string }) {
  return flagged ? (
    <span className={styles.stateFlag}>
      <FlagIcon />
      {flagText}
    </span>
  ) : (
    <span className={styles.stateOk}>
      <CheckIcon />
      {okText}
    </span>
  );
}

/** A row of squares: filled = left, hollow = used. The same pictogram as the waffle charts. */
export function Squares({ filled, total, label }: { filled: number; total: number; label: string }) {
  return (
    <span className={styles.squares} role="img" aria-label={label}>
      {Array.from({ length: total }, (_, i) => (
        <span key={i} className={i < filled ? styles.sqOn : styles.sqOff} />
      ))}
    </span>
  );
}

export function PageHead({ title, lede }: { title: string; lede?: string }) {
  return (
    <header className={styles.pageHead}>
      <h1 className={styles.h1}>{title}</h1>
      {lede ? <p className={styles.lede}>{lede}</p> : null}
    </header>
  );
}

/** Margin-note layout: the heading stands in the margin, the content beside it. */
export function Row({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className={styles.row} aria-label={title}>
      <h2 className={styles.rowHead}>{title}</h2>
      <div className={styles.rowBody}>{children}</div>
    </section>
  );
}

export function EmptyState({
  title,
  body,
  action,
}: {
  title: string;
  body: string;
  action?: { label: string; href?: string; onClick?: () => void };
}) {
  return (
    <div className={styles.empty}>
      <p className={styles.emptyTitle}>{title}</p>
      <p className={styles.emptyBody}>{body}</p>
      {action ? (
        action.href ? (
          <Link href={action.href} className={styles.primary}>
            {action.label}
          </Link>
        ) : (
          <button type="button" className={styles.secondary} onClick={action.onClick}>
            {action.label}
          </button>
        )
      ) : null}
    </div>
  );
}
