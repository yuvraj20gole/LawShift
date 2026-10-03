"use client";

import type { CSSProperties, ElementType, ReactNode } from "react";
import { useReveal } from "@/hooks/useReveal";

type Props = {
  children: ReactNode;
  className?: string;
  /** Stagger index for cascade (trust cards, how-it-works steps). */
  index?: number;
  as?: "div" | "section" | "article" | "li";
};

export function Reveal({ children, className = "", index = 0, as = "div" }: Props) {
  const { ref, visible, style } = useReveal({ index });
  const Tag = as as ElementType;

  return (
    <Tag
      ref={ref}
      className={`reveal ${visible ? "revealVisible" : ""} ${className}`.trim()}
      style={style as CSSProperties}
    >
      {children}
    </Tag>
  );
}
