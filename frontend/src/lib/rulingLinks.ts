import type { DashboardCopy } from "./dashboardCopy";

/** Name of a site from its url, for linkKind "other" when no siteName is given. */
export function hostOf(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

/**
 * The link text for a ruling, from its linkKind:
 * "court" -> the court's copy; "archive" -> archive copy; "other" -> a copy on
 * another site, named.
 */
export function linkLabel(
  C: DashboardCopy,
  kind: "court" | "archive" | "other",
  url: string,
  siteName?: string,
): string {
  if (kind === "court") return C.linkCourt;
  if (kind === "archive") return C.linkArchive;
  return C.linkOther(siteName || hostOf(url));
}
