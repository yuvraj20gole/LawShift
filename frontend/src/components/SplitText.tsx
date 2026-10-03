"use client";

import { Fragment, type CSSProperties, type ElementType } from "react";
import { useInView } from "@/hooks/useInView";
import styles from "./SplitText.module.css";

type Props = {
  text: string;
  as?: ElementType;
  className?: string;
  /** Play on page load instead of when scrolled into view. */
  immediate?: boolean;
  /** Extra delay before the first word, in ms. */
  delay?: number;
};

/**
 * Words rise out of a mask one after another. The full sentence stays
 * available to assistive tech; the split words are hidden from it.
 */
export function SplitText({ text, as: Tag = "span", className = "", immediate, delay = 0 }: Props) {
  const { ref, pending } = useInView<HTMLElement>(0.35);
  const words = text.split(" ");

  return (
    <Tag
      ref={ref}
      className={`${styles.split} ${immediate ? styles.immediate : ""} ${className}`.trim()}
      data-pending={!immediate && pending ? "true" : undefined}
    >
      <span className="sr-only">{text}</span>
      {words.map((w, i) => (
        <Fragment key={i}>
          <span className={styles.w} aria-hidden>
            <span
              className={styles.wi}
              style={{ ["--i" as string]: i, ["--base" as string]: `${delay}ms` } as CSSProperties}
            >
              {w}
            </span>
          </span>
          {i < words.length - 1 ? " " : null}
        </Fragment>
      ))}
    </Tag>
  );
}
