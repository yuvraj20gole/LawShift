"use client";

import { useEffect, useRef } from "react";
import styles from "./Header.module.css";

/** A thin bronze bar along the header edge that tracks how far down the page you are. */
export function ScrollProgress() {
  const bar = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    let raf = 0;
    const update = () => {
      raf = 0;
      const el = document.documentElement;
      const max = el.scrollHeight - el.clientHeight;
      const p = max > 0 ? Math.min(1, el.scrollTop / max) : 0;
      if (bar.current) bar.current.style.transform = `scaleX(${p})`;
      el.dataset.scrolled = el.scrollTop > 8 ? "true" : "false";
    };
    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(update);
    };
    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);

  return <span ref={bar} className={styles.progress} aria-hidden />;
}
