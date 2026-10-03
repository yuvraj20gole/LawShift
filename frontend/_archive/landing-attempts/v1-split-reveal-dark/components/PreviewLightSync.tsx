"use client";

import { Suspense, useEffect } from "react";
import { useSearchParams } from "next/navigation";

/**
 * Temporary review hook: `?preview=light` applies a warm paper light palette
 * for side-by-side comparison. Not a shipped theme toggle.
 */
function PreviewLightSyncInner() {
  const searchParams = useSearchParams();

  useEffect(() => {
    const preview = searchParams.get("preview");
    if (preview === "light") {
      document.documentElement.setAttribute("data-preview", "light");
    } else {
      document.documentElement.removeAttribute("data-preview");
    }
    return () => {
      document.documentElement.removeAttribute("data-preview");
    };
  }, [searchParams]);

  return null;
}

export function PreviewLightSync() {
  return (
    <Suspense fallback={null}>
      <PreviewLightSyncInner />
    </Suspense>
  );
}
