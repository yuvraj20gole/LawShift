"use client";

import type { ReactNode } from "react";
import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion";

type Props = {
  children: ReactNode;
  className?: string;
  /** Pixels of vertical travel over the first 700px of scroll. */
  from?: number;
  to?: number;
};

/** Drifts its content at its own speed while the hero scrolls away. */
export function Parallax({ children, className, from = 0, to = -60 }: Props) {
  const reduce = useReducedMotion();
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 700], [from, to]);
  return (
    <motion.div className={className} style={reduce ? undefined : { y }}>
      {children}
    </motion.div>
  );
}
