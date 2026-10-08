"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { Rise } from "@/components/Rise";
import { SplitText } from "@/components/SplitText";
import styles from "./dashboard.module.css";
import { CheckIcon, FlagIcon } from "@/components/auth/AuthParts";
import type { Code } from "@/lib/sampleData";

/** IPC slate / BNS navy: the same two code colours as the landing page. */
export function CodeBadge({ code }: { code: Code | string }) {
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

export function PageHead({ title, lede }: { title: string; lede?: string }) {
  return (
    <header className={styles.pageHead}>
      <h1 className={styles.h1}>
        <SplitText immediate text={title} />
      </h1>
      {lede ? <p className={styles.lede}>{lede}</p> : null}
    </header>
  );
}

/** Margin-note layout: the heading stands in the margin, the content beside it. */
export function Row({
  title,
  children,
  tone,
}: {
  title: string;
  children: ReactNode;
  /** "real" marks the one block that shows real archive data. */
  tone?: "real";
}) {
  return (
    <Rise
      as="section"
      aria-label={title}
      threshold={0.12}
      className={`${styles.row} ${tone === "real" ? styles.rowReal : ""}`}
    >
      <h2 className={styles.rowHead}>{title}</h2>
      <div className={styles.rowBody}>{children}</div>
    </Rise>
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
