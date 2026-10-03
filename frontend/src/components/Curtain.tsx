"use client";

import { useRef, type ReactNode } from "react";
import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion";

type Props = {
  id: string;
  className?: string;
  labelledBy?: string;
  children: ReactNode;
};

/**
 * A full-bleed band that opens like a curtain: it starts inset from both
 * sides with rounded top corners and widens to the full screen as it scrolls
 * up into place.
 */
export function Curtain({ id, className, labelledBy, children }: Props) {
  const ref = useRef<HTMLElement>(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "start 25%"],
  });
  const inset = useTransform(scrollYProgress, [0, 1], [7, 0]);
  const radius = useTransform(scrollYProgress, [0, 1], [64, 0]);
  const clip = useTransform(
    [inset, radius],
    ([i, r]) => `inset(0 ${i}% 0 ${i}% round ${r}px ${r}px 0 0)`,
  );

  return (
    <motion.section
      ref={ref}
      id={id}
      className={className}
      aria-labelledby={labelledBy}
      style={reduce ? undefined : { clipPath: clip }}
    >
      {children}
    </motion.section>
  );
}
