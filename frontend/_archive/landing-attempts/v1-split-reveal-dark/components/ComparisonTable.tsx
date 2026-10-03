"use client";

import { Reveal } from "./Reveal";
import { useT } from "@/lib/prefs";
import styles from "./ComparisonTable.module.css";

type Cell = "yes" | "no" | "partial";

export function ComparisonTable() {
  const t = useT();

  const cols = [t.colStatic, t.colDense, t.colLawShift];
  const rows: {
    feature: string;
    cells: { kind: Cell; text: string }[];
  }[] = [
    {
      feature: t.rowArt20,
      cells: [
        { kind: "partial", text: t.cellManual },
        { kind: "no", text: t.cellModel },
        { kind: "yes", text: t.cellHardGate },
      ],
    },
    {
      feature: t.rowBifurcation,
      cells: [
        { kind: "no", text: t.cellSingleHit },
        { kind: "no", text: t.cellSilentTop },
        { kind: "yes", text: t.cellScoreGap },
      ],
    },
    {
      feature: t.rowTrace,
      cells: [
        { kind: "partial", text: t.cellTableOnly },
        { kind: "no", text: t.cellOpaque },
        { kind: "yes", text: t.cellCascade },
      ],
    },
    {
      feature: t.rowPlain,
      cells: [
        { kind: "no", text: t.cellRawStatute },
        { kind: "partial", text: t.cellUnconstrained },
        { kind: "yes", text: t.cellConstrainedIrac },
      ],
    },
    {
      feature: t.rowHallucination,
      cells: [
        { kind: "yes", text: t.cellLowNoGen },
        { kind: "no", text: t.cellHigh },
        { kind: "yes", text: t.cellZeroFab },
      ],
    },
  ];

  return (
    <section className={styles.section} aria-labelledby="compare-heading">
      <div className="container">
        <Reveal>
          <h2 id="compare-heading" className={styles.heading}>
            {t.compareHeading}
          </h2>
          <p className={styles.lede}>{t.compareLede}</p>
        </Reveal>
        <Reveal index={1}>
          <div className={styles.scroll}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th scope="col">{t.compareCapability}</th>
                  {cols.map((c) => (
                    <th
                      key={c}
                      scope="col"
                      className={c === t.colLawShift ? styles.hl : undefined}
                    >
                      {c}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.feature}>
                    <th scope="row">{row.feature}</th>
                    {row.cells.map((cell, i) => (
                      <td key={`${row.feature}-${i}`} className={i === 2 ? styles.hl : undefined}>
                        <span
                          className={
                            cell.kind === "yes"
                              ? styles.yes
                              : cell.kind === "no"
                                ? styles.no
                                : styles.partial
                          }
                        >
                          {cell.text}
                        </span>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
