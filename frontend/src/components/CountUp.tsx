"use client";

import { useEffect, useRef, useState } from "react";
import { useInView } from "@/hooks/useInView";

/**
 * Counts every number in `text` up from zero once the element scrolls into
 * view, ending on exactly the original string. Renders the final text on the
 * server and without JS or with reduced motion.
 */
export function CountUp({ text, className }: { text: string; className?: string }) {
  const { ref, pending, seen } = useInView<HTMLSpanElement>(0.5);
  const [t, setT] = useState(1);
  const zeroed = useRef(false);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    if (pending) {
      zeroed.current = true;
      setT(0);
    }
  }, [pending]);

  useEffect(() => {
    if (!seen || !zeroed.current) return;
    let raf = 0;
    const start = performance.now();
    const dur = 1400;
    const tick = (now: number) => {
      const p = Math.min(1, (now - start) / dur);
      setT(1 - Math.pow(1 - p, 4));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [seen]);

  const out = text.replace(/\d+/g, (n) => String(Math.round(Number(n) * t)));
  return (
    <span ref={ref} className={className} aria-label={text}>
      <span aria-hidden style={{ fontVariantNumeric: "tabular-nums lining-nums" }}>
        {out}
      </span>
    </span>
  );
}
