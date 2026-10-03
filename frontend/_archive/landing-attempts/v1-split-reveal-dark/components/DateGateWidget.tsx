"use client";

import { useMemo, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { useT } from "@/lib/prefs";
import styles from "./DateGateWidget.module.css";

/** Matches Stage 2 cutoff in app/stage2.py / src/stage1_entity_extraction.py */
const CUTOFF = new Date(2024, 6, 1); // 1 July 2024 local

function routeForDate(iso: string): "IPC" | "BNS" | null {
  if (!iso) return null;
  const [y, m, d] = iso.split("-").map(Number);
  if (!y || !m || !d) return null;
  const picked = new Date(y, m - 1, d);
  return picked < CUTOFF ? "IPC" : "BNS";
}

export function DateGateWidget() {
  const t = useT();
  const reduce = useReducedMotion();
  const [date, setDate] = useState("2024-07-01");
  const route = useMemo(() => routeForDate(date), [date]);

  return (
    <aside className={styles.widget} aria-label="Deterministic routing demonstration">
      <div className={styles.top}>
        <p className={styles.label}>{t.offenseDate}</p>
        <p className={styles.cutoff}>
          {t.cutoffLabel} <span className="serif">1 July 2024</span>
        </p>
      </div>

      <label className={styles.field}>
        <span className={styles.srLabel}>{t.pickOffenseDate}</span>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          min="1860-01-01"
          max="2030-12-31"
          className={styles.input}
        />
      </label>

      <div className={styles.result}>
        <p className={styles.resultLabel}>{t.applies}</p>
        <div className={styles.badgeSlot}>
          <AnimatePresence mode="wait" initial={false}>
            {route ? (
              <motion.div
                key={route}
                className={route === "IPC" ? styles.badgeIpc : styles.badgeBns}
                role="status"
                aria-live="polite"
                initial={reduce ? { opacity: 0 } : { opacity: 0, scale: 0.86 }}
                animate={reduce ? { opacity: 1 } : { opacity: 1, scale: 1 }}
                exit={reduce ? { opacity: 0 } : { opacity: 0, scale: 0.92 }}
                transition={
                  reduce
                    ? { duration: 0.12 }
                    : { type: "spring", stiffness: 420, damping: 22, mass: 0.7 }
                }
              >
                {route}
              </motion.div>
            ) : (
              <div className={styles.badgeEmpty}>—</div>
            )}
          </AnimatePresence>
        </div>
      </div>

      <p className={styles.note} key={route ?? "empty"}>
        {route === "IPC" ? t.noteIpc : route === "BNS" ? t.noteBns : t.noteEmpty}
      </p>

      <p className={styles.fine}>{t.gateFine}</p>
    </aside>
  );
}
