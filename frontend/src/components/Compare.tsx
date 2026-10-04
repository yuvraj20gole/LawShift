"use client";

import { usePrefs } from "@/lib/prefs";
import { useInView } from "@/hooks/useInView";
import { getLandingCopy } from "@/lib/landingCopy";
import { CodeCompare, type CardData } from "./CodeCompare";
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

export function Compare() {
  const { lang } = usePrefs();
  const L = getLandingCopy(lang);
  const { ref, pending } = useInView<HTMLElement>(0.3);

  const toCard = (d: typeof IPC, span: string): CardData => ({
    id: d.code,
    code: d.code === "IPC 292" ? "IPC" : "BNS",
    title: d.code,
    heading: d.heading,
    span,
    rows: [
      { label: L.compareRow1, segs: d.row1 },
      { label: L.compareRow2, segs: d.row2 },
    ],
  });

  return (
    <CodeCompare
      as="figure"
      rootRef={ref}
      className={pending ? styles.pending : ""}
      left={[toCard(IPC, L.compareIpcSpan)]}
      right={[toCard(BNS, L.compareBnsSpan)]}
      swapLabel={L.compareSwap}
    >
      <figcaption className={styles.note}>
        <span>{L.compareMapped}</span> <span>{L.compareChanged}</span>
        <span className={styles.source}>{L.compareSource}</span>
      </figcaption>
    </CodeCompare>
  );
}
