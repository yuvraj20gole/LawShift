"use client";

import { Fragment, type ElementType, type ReactNode, type Ref } from "react";
import { SwapIcon } from "./StepIcons";
import type { Seg } from "@/lib/wordDiff";
import styles from "./Compare.module.css";

export type CardRow = { label?: string; segs: Seg[]; scroll?: boolean };

export type CardData = {
  id: string;
  code: "IPC" | "BNS";
  title: string;
  heading: string;
  span?: string;
  rows: CardRow[];
  note?: string;
};

function Excerpt({ segs, tone, scroll }: { segs: Seg[]; tone: "ipc" | "bns"; scroll?: boolean }) {
  return (
    <p className={`${styles.excerpt} ${scroll ? styles.scrollText : ""}`} {...(scroll ? { "data-lenis-prevent": true, tabIndex: 0 } : {})}>
      {segs.map((s, i) => (
        <Fragment key={i}>
          {s.hl ? <mark className={tone === "ipc" ? styles.hlIpc : styles.hlBns}>{s.t}</mark> : s.t}
        </Fragment>
      ))}
    </p>
  );
}

function Card({ d }: { d: CardData }) {
  const tone = d.code === "IPC" ? "ipc" : "bns";
  return (
    <article className={`${styles.card} ${tone === "ipc" ? styles.cardIpc : styles.cardBns}`}>
      <header className={styles.cardHead}>
        <h3 className={`${styles.code} ${tone === "ipc" ? styles.ipc : styles.bns}`}>{d.title}</h3>
        <p className={styles.heading}>{d.heading}</p>
        {d.span ? <p className={styles.span}>{d.span}</p> : null}
      </header>
      {d.note ? <p className={styles.cardNote}>{d.note}</p> : null}
      <dl className={styles.rows}>
        {d.rows.map((r, i) => (
          <div key={i} className={styles.row}>
            {r.label ? <dt>{r.label}</dt> : null}
            <dd>
              <Excerpt segs={r.segs} tone={tone} scroll={r.scroll} />
            </dd>
          </div>
        ))}
      </dl>
    </article>
  );
}

/**
 * The "Same offence, two codes" comparison, reusable: any number of cards on
 * each side, a bronze cutoff line between them, and highlights only where the
 * caller marks words as different.
 */
export function CodeCompare({
  left,
  right,
  swapLabel,
  as: Tag = "div",
  className = "",
  rootRef,
  leftEmpty,
  rightEmpty,
  children,
}: {
  left: CardData[];
  right: CardData[];
  swapLabel: string;
  as?: ElementType;
  className?: string;
  rootRef?: Ref<HTMLElement>;
  /** Shown in the left / right column when that side has no card. */
  leftEmpty?: ReactNode;
  rightEmpty?: ReactNode;
  children?: ReactNode;
}) {
  return (
    <Tag ref={rootRef} className={`${styles.compare} ${className}`.trim()}>
      <div className={styles.col}>
        {left.length ? left.map((d) => <Card key={d.id} d={d} />) : leftEmpty}
      </div>

      <div className={styles.swap} aria-hidden>
        <span className={styles.swapLine} />
        <span className={styles.swapMark}>
          <SwapIcon />
          <span>{swapLabel}</span>
        </span>
        <span className={styles.swapLine} />
      </div>

      <div className={styles.col}>
        {right.length ? right.map((d) => <Card key={d.id} d={d} />) : rightEmpty}
      </div>

      {children}
    </Tag>
  );
}
