import { useEffect, useRef, useState } from "react";

/**
 * `pending` is true only after hydration and until the element first scrolls
 * into view, so server-rendered and no-JS content is never hidden.
 */
export function useInView<T extends HTMLElement>(threshold = 0.25) {
  const ref = useRef<T>(null);
  const [seen, setSeen] = useState(false);
  const [armed, setArmed] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el || seen) return;
    if (typeof IntersectionObserver === "undefined") {
      setSeen(true);
      return;
    }
    setArmed(true);
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setSeen(true);
          io.disconnect();
        }
      },
      { threshold },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [seen, threshold]);

  return { ref, seen, pending: armed && !seen };
}
