"use client";

import { usePrefs } from "@/lib/prefs";
import { getLandingCopy } from "@/lib/landingCopy";
import { getLenis } from "@/lib/lenisRef";
import styles from "./Docket.module.css";

/**
 * Three cases from the backend's own smoke runs (PROCESS_LOG §18; the third
 * re-checked live against /api/query, which offers BNS 180 and BNS 179), stacked in
 * time order with the 1 July 2024 cutoff drawn between the first and the
 * rest. Display copy is translated; `ask` stays English so the live pipeline
 * receives the recorded query text.
 */
const CASE_ASK = [
  "On 25 June 2024, a bookstore owner sold obscene magazines for the first time.",
  "On 10 August 2024, a riot occurred for a landowner's benefit and the agent failed to prevent it.",
  "On 5 September 2024, a person was found in possession of counterfeit currency notes.",
] as const;

function ask(text: string) {
  window.dispatchEvent(new CustomEvent("lawshift:ask", { detail: { text } }));
  const chat = document.getElementById("chat");
  const lenis = getLenis();
  if (lenis) {
    lenis.scrollTo("#chat", { offset: -64, duration: 1.6 });
    return;
  }
  chat?.scrollIntoView({
    behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
      ? "auto"
      : "smooth",
    block: "start",
  });
}

export function Docket() {
  const { lang } = usePrefs();
  const L = getLandingCopy(lang);

  const cases = [
    {
      law: "IPC" as const,
      date: "25 June 2024",
      facts: L.case1Facts,
      result: "IPC 292",
      resultNote: L.case1ResultNote,
      ask: CASE_ASK[0],
    },
    {
      law: "BNS" as const,
      date: "10 August 2024",
      facts: L.case2Facts,
      result: "BNS 193",
      resultNote: L.case2ResultNote,
      ask: CASE_ASK[1],
    },
    {
      law: "BNS" as const,
      date: "5 September 2024",
      facts: L.case3Facts,
      result: "BNS 180 or 179",
      resultNote: L.case3ResultNote,
      ask: CASE_ASK[2],
    },
  ];

  const card = (c: (typeof cases)[number], i: number) => (
    <li
      key={c.date}
      className={`${styles.cell} ${c.law === "IPC" ? styles.cellIpc : styles.cellBns}`}
      style={{ ["--i" as string]: i }}
    >
      <button type="button" className={styles.case} onClick={() => ask(c.ask)}>
        <span className={styles.top}>
          <span className={styles.date}>{c.date}</span>
          <span className={`${styles.tag} ${c.law === "IPC" ? styles.tagIpc : styles.tagBns}`}>
            {c.law === "IPC" ? L.docketIpcName : L.docketBnsName}
          </span>
        </span>
        <span className={styles.facts}>{c.facts}</span>
        <span className={styles.resultRow}>
          <span className={`${styles.result} ${c.law === "IPC" ? styles.ipc : styles.bns}`}>
            {c.result}
          </span>
          <span className={styles.try}>{L.docketTry}</span>
          <span className={styles.resultNote}>{c.resultNote}</span>
        </span>
      </button>
    </li>
  );

  return (
    <figure className={styles.panel}>
      <ol className={styles.list} role="list">
        {card(cases[0], 0)}
        <li className={styles.cutoff} aria-hidden>
          <span className={styles.cutLine} />
          <span className={styles.cutPill}>1 July 2024</span>
          <span className={styles.cutLine} />
        </li>
        {card(cases[1], 1)}
        {card(cases[2], 2)}
      </ol>
      <figcaption className={styles.caption}>{L.docketCaption}</figcaption>
    </figure>
  );
}
