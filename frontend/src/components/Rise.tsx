"use client";

import type { CSSProperties, ElementType, ReactNode } from "react";
import { useInView } from "@/hooks/useInView";
import styles from "./Rise.module.css";

type Props = {
  children: ReactNode;
  as?: ElementType;
  className?: string;
  /** Position in a group; each step adds a short stagger. */
  index?: number;
  threshold?: number;
  "aria-label"?: string;
};

/**
 * Reveals its content once, when it first scrolls into view. Content is
 * visible in server-rendered HTML and without JS; it is only hidden after
 * hydration, and never under prefers-reduced-motion.
 */
export function Rise({
  children,
  as: Tag = "div",
  className = "",
  index = 0,
  threshold = 0.2,
  "aria-label": ariaLabel,
}: Props) {
  const { ref, pending } = useInView<HTMLElement>(threshold);
  return (
    <Tag
      ref={ref}
      className={`${styles.rise} ${className}`.trim()}
      aria-label={ariaLabel}
      data-pending={pending ? "true" : undefined}
      style={{ ["--d" as string]: index } as CSSProperties}
    >
      {children}
    </Tag>
  );
}
