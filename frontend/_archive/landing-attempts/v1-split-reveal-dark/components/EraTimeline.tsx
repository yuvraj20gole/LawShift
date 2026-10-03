"use client";

import { useEffect, useId, useMemo, useState } from "react";
import styles from "./EraTimeline.module.css";

type Props = {
  /** "section" = full-width dedicated treatment; default is compact */
  variant?: "compact" | "section";
};

/**
 * Horizontal IPC→BNS timeline: draws on load, marker travels to "today."
 */
export function EraTimeline({ variant = "compact" }: Props) {
  const uid = useId().replace(/:/g, "");
  const [drawn, setDrawn] = useState(false);
  const [reduceMotion, setReduceMotion] = useState(false);
  const isSection = variant === "section";

  const layout = useMemo(() => {
    const W = 1000;
    const H = isSection ? 120 : 72;
    const y = isSection ? 58 : 36;
    const x0 = isSection ? 24 : 48;
    const x1 = W - (isSection ? 24 : 48);
    const span = x1 - x0;
    const cutoffX = x0 + span * 0.62;
    const todayX = x0 + span * 0.88;
    return { W, H, y, x0, x1, cutoffX, todayX, travel: todayX - x0 };
  }, [isSection]);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduceMotion(mq.matches);
    if (mq.matches) {
      setDrawn(true);
      return;
    }
    const t = window.setTimeout(() => setDrawn(true), 60);
    return () => window.clearTimeout(t);
  }, []);

  const { W, H, y, x0, x1, cutoffX, todayX, travel } = layout;
  const trackW = isSection ? 6 : 2;
  const segIpcW = isSection ? 6 : 3;
  const segBnsW = isSection ? 7 : 3.5;
  const markerR = isSection ? 8 : 5.5;

  return (
    <div
      className={`${styles.wrap} ${isSection ? styles.sectionWrap : ""} ${drawn ? styles.drawn : ""} ${reduceMotion ? styles.static : ""}`}
      aria-hidden="true"
    >
      <svg
        className={`${styles.svg} ${isSection ? styles.sectionSvg : ""}`}
        viewBox={`0 0 ${W} ${H}`}
        preserveAspectRatio="xMidYMid meet"
        role="presentation"
      >
        <defs>
          <linearGradient id={`ipcGrad-${uid}`} x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="var(--timeline-ipc)" stopOpacity="0.3" />
            <stop offset="100%" stopColor="var(--timeline-ipc)" stopOpacity="0.65" />
          </linearGradient>
          <linearGradient id={`bnsGrad-${uid}`} x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="var(--timeline-bns)" stopOpacity="0.5" />
            <stop offset="100%" stopColor="var(--timeline-bns)" stopOpacity="1" />
          </linearGradient>
        </defs>

        <line
          className={styles.track}
          x1={x0}
          y1={y}
          x2={x1}
          y2={y}
          stroke="var(--timeline-track)"
          strokeWidth={trackW}
          strokeLinecap="round"
        />

        <line
          className={styles.segIpc}
          x1={x0}
          y1={y}
          x2={cutoffX}
          y2={y}
          stroke={`url(#ipcGrad-${uid})`}
          strokeWidth={segIpcW}
          strokeLinecap="round"
          pathLength={1}
        />

        <line
          className={styles.segBns}
          x1={cutoffX}
          y1={y}
          x2={todayX}
          y2={y}
          stroke={`url(#bnsGrad-${uid})`}
          strokeWidth={segBnsW}
          strokeLinecap="round"
          pathLength={1}
        />

        <g className={styles.cutoff}>
          <line
            x1={cutoffX}
            y1={y - (isSection ? 18 : 11)}
            x2={cutoffX}
            y2={y + (isSection ? 18 : 11)}
            stroke="var(--timeline-cutoff)"
            strokeWidth={isSection ? 2.5 : 1.5}
          />
          <circle
            cx={cutoffX}
            cy={y}
            r={isSection ? 5 : 3.25}
            fill="var(--timeline-cutoff)"
          />
        </g>

        <g
          className={styles.markerGroup}
          style={{ ["--travel" as string]: `${travel}px` }}
        >
          <circle
            className={styles.marker}
            cx={x0}
            cy={y}
            r={markerR}
            fill="var(--timeline-marker)"
          />
        </g>

        <text
          className={`${styles.labelIpc} ${isSection ? styles.labelLg : ""}`}
          x={x0}
          y={y - (isSection ? 28 : 16)}
        >
          IPC · 1860
        </text>
        <text
          className={`${styles.labelCut} ${isSection ? styles.labelLg : ""}`}
          x={cutoffX}
          y={y + (isSection ? 38 : 24)}
          textAnchor="middle"
        >
          1 July 2024
        </text>
        <text
          className={`${styles.labelBns} ${isSection ? styles.labelLg : ""}`}
          x={todayX}
          y={y - (isSection ? 28 : 16)}
          textAnchor="middle"
        >
          BNS · today
        </text>
      </svg>
    </div>
  );
}
