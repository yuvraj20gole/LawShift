/** Accepts a same-site path only: one leading "/", no "//", no backslash, no scheme or control characters. */
export function safeNext(raw: string | null | undefined): string | null {
  if (!raw) return null;
  if (!raw.startsWith("/") || raw.startsWith("//")) return null;
  if (/[\\\u0000-\u001f]/.test(raw)) return null;
  try {
    const u = new URL(raw, "http://lawshift.invalid");
    if (u.origin !== "http://lawshift.invalid") return null;
  } catch {
    return null;
  }
  return raw;
}
