"use client";

import { useRef, type ReactNode } from "react";
import {
  motion,
  useReducedMotion,
  useScroll,
  useSpring,
  useTransform,
  type MotionValue,
} from "framer-motion";
import styles from "../app/landing.module.css";

function RailStep({
  p,
  i,
  count,
  children,
}: {
  p: MotionValue<number>;
  i: number;
  count: number;
  children: ReactNode;
}) {
  const reduce = useReducedMotion();
  const start = (i / count) * 0.8;
  const opacity = useTransform(p, [start, start + 0.14], [0.3, 1]);
  const y = useTransform(p, [start, start + 0.14], [24, 0]);
  return (
    <motion.li className={styles.railStep} style={reduce ? undefined : { opacity, y }}>
      {children}
    </motion.li>
  );
}

/**
 * The four steps light up one after another as you scroll through them. The
 * line between them is drawn by your scroll position, not by a timer.
 */
export function ScrubRail({ steps }: { steps: ReactNode[] }) {
  const ref = useRef<HTMLOListElement>(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start 80%", "end 60%"] });
  const p = useSpring(scrollYProgress, { stiffness: 110, damping: 28, mass: 0.4 });
  const fill = useTransform(p, [0, 0.85], [0, 1]);

  return (
    <div className={styles.railWrap}>
      <ol ref={ref} className={styles.rail}>
        {steps.map((node, i) => (
          <RailStep key={i} p={p} i={i} count={steps.length}>
            {node}
          </RailStep>
        ))}
      </ol>
      <span className={styles.railTrack} aria-hidden />
      <motion.span
        className={styles.railFill}
        style={reduce ? { transform: "scaleX(1)" } : { scaleX: fill }}
        aria-hidden
      />
    </div>
  );
}
