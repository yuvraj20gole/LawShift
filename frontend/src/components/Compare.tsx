"use client";

import { Fragment } from "react";
import { usePrefs } from "@/lib/prefs";
import { useInView } from "@/hooks/useInView";
import { getLandingCopy } from "@/lib/landingCopy";
import { SwapIcon } from "./StepIcons";
import styles from "./Compare.module.css";

/**
 * IPC 292 → BNS 294, quoted from data/clean/mapping.jsonl
 * (nandhakumarg/IPC_and_BNS_transformation, mapping_type "section").
 * Statute wording stays in English; `hl` marks words that differ between
 * the two texts. Ellipses mark omitted words; footnote markers are removed.
 */
type Seg = { t: string; hl?: boolean };

const IPC = {
  code: "IPC 292",
  heading: "Sale, etc., of obscene books, etc.",
  row1: [
    {
      t: "… a book, pamphlet, paper, writing, drawing, painting, representation, figure or any other object, shall be deemed to be obscene if it is lascivious or appeals to the prurient interest …",
    },
  ] as Seg[],
  row2: [
    {
      t: "… shall be punished on first conviction with imprisonment of either description for a term which may extend to two years, and with fine which may extend to ",
    },
    { t: "two thousand rupees", hl: true },
    { t: " …" },
  ] as Seg[],
};

const BNS = {
  code: "BNS 294",
  heading: "Sale, etc., of obscene books, etc.",
  row1: [
    {
      t: "… a book, pamphlet, paper, writing, drawing, painting, representation, figure or any other object, ",
    },
    { t: "including display of any content in electronic form", hl: true },
    {
      t: " shall be deemed to be obscene if it is lascivious or appeals to the prurient interest …",
    },
  ] as Seg[],
  row2: [
    {
      t: "… shall be punished on first conviction with imprisonment of either description for a term which may extend to two years, and with fine which may extend to ",
    },
    { t: "five thousand rupees", hl: true },
    { t: " …" },
  ] as Seg[],
};

function Excerpt({ segs, tone }: { segs: Seg[]; tone: "ipc" | "bns" }) {
  return (
    <p className={styles.excerpt}>
      {segs.map((s, i) => (
        <Fragment key={i}>
          {s.hl ? (
            <mark className={tone === "ipc" ? styles.hlIpc : styles.hlBns}>{s.t}</mark>
          ) : (
            s.t
          )}
        </Fragment>
      ))}
    </p>
  );
}

export function Compare() {
  const { lang } = usePrefs();
  const L = getLandingCopy(lang);
  const { ref, pending } = useInView<HTMLElement>(0.3);

  const card = (
    d: typeof IPC,
    tone: "ipc" | "bns",
    span: string,
    cls: string,
  ) => (
    <article className={`${styles.card} ${cls}`}>
      <header className={styles.cardHead}>
        <h3 className={`${styles.code} ${tone === "ipc" ? styles.ipc : styles.bns}`}>{d.code}</h3>
        <p className={styles.heading}>{d.heading}</p>
        <p className={styles.span}>{span}</p>
      </header>
      <dl className={styles.rows}>
        <div className={styles.row}>
          <dt>{L.compareRow1}</dt>
          <dd>
            <Excerpt segs={d.row1} tone={tone} />
          </dd>
        </div>
        <div className={styles.row}>
          <dt>{L.compareRow2}</dt>
          <dd>
            <Excerpt segs={d.row2} tone={tone} />
          </dd>
        </div>
      </dl>
    </article>
  );

  return (
    <figure ref={ref} className={`${styles.compare} ${pending ? styles.pending : ""}`}>
      {card(IPC, "ipc", L.compareIpcSpan, styles.cardIpc)}

      <div className={styles.swap} aria-hidden>
        <span className={styles.swapLine} />
        <span className={styles.swapMark}>
          <SwapIcon />
          <span>{L.compareSwap}</span>
        </span>
        <span className={styles.swapLine} />
      </div>

      {card(BNS, "bns", L.compareBnsSpan, styles.cardBns)}

      <figcaption className={styles.note}>
        <span>{L.compareMapped}</span> <span>{L.compareChanged}</span>
        <span className={styles.source}>{L.compareSource}</span>
      </figcaption>
    </figure>
  );
}
