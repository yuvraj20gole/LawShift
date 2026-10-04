"use client";

import { useId, type ReactNode } from "react";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import styles from "./dashboard.module.css";

/** The tooltip wording for a bench: never states or guesses what an unlabelled code is. */
export function useBenchTip(code: string, label: string | null | undefined) {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);
  return label ? C.benchTip(code) : C.benchTipNone;
}

/** A focusable bench name with a tooltip on hover and on keyboard focus. */
export function BenchTip({
  code,
  label,
  children,
  as: Wrap = "span",
}: {
  code: string;
  label: string | null | undefined;
  children?: ReactNode;
  as?: "span" | "div";
}) {
  const id = useId();
  const tip = useBenchTip(code, label);
  return (
    <Wrap className={styles.tip} tabIndex={0} aria-describedby={id}>
      {children ?? label ?? code}
      <span id={id} role="tooltip" className={styles.tipText}>
        {tip}
      </span>
    </Wrap>
  );
}
