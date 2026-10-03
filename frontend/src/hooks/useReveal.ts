import { useEffect, useRef, useState, type CSSProperties } from "react";

type Options = {
  /** Stagger index for cascade delays (0-based). */
  index?: number;
  /** Root margin so reveals fire slightly before fully in view. */
  rootMargin?: string;
  threshold?: number;
};

/**
 * IntersectionObserver-based reveal. Respects prefers-reduced-motion
 * by starting already-visible when the media query matches.
 * Also reveals elements already above or in the viewport (covers
 * instant scroll jumps that skip IO intersection frames).
 */
export function useReveal<T extends HTMLElement = HTMLElement>({
  index = 0,
  rootMargin = "0px 0px -6% 0px",
  threshold = 0.05,
}: Options = {}) {
  const ref = useRef<T | null>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      setVisible(true);
      return;
    }

    const revealIfPast = () => {
      const rect = el.getBoundingClientRect();
      // Already in or above the visible band
      if (rect.top < window.innerHeight * 0.94) {
        setVisible(true);
        return true;
      }
      return false;
    };

    if (revealIfPast()) return;

    const io = new IntersectionObserver(
      ([entry]) => {
        if (!entry) return;
        if (entry.isIntersecting || entry.boundingClientRect.top < window.innerHeight) {
          setVisible(true);
          io.disconnect();
        }
      },
      { rootMargin, threshold },
    );

    io.observe(el);
    return () => io.disconnect();
  }, [rootMargin, threshold]);

  return {
    ref,
    visible,
    style: {
      ["--reveal-delay" as string]: `${index * 100}ms`,
    } as CSSProperties,
  };
}
