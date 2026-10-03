"use client";

import { useEffect } from "react";
import Lenis from "lenis";
import { setLenis } from "@/lib/lenisRef";

/** Inertial page scrolling. Skipped entirely for people who ask for reduced motion. */
export function SmoothScroll() {
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const lenis = new Lenis({
      duration: 1.2,
      easing: (t: number) => 1 - Math.pow(1 - t, 4),
      anchors: { offset: -64, duration: 1.4 },
    });
    setLenis(lenis);

    let raf = requestAnimationFrame(function loop(time) {
      lenis.raf(time);
      raf = requestAnimationFrame(loop);
    });

    return () => {
      cancelAnimationFrame(raf);
      lenis.destroy();
      setLenis(null);
    };
  }, []);

  return null;
}
