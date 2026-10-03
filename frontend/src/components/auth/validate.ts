/** Standard email shape: something@something.tld (no spaces). */
export const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export function isEmail(v: string) {
  return EMAIL_RE.test(v.trim());
}

/** The five password rules, in the order they are shown. */
export const PASSWORD_RULES = [
  { id: "len", test: (p: string) => p.length >= 8 },
  { id: "upper", test: (p: string) => /[A-Z]/.test(p) },
  { id: "lower", test: (p: string) => /[a-z]/.test(p) },
  { id: "digit", test: (p: string) => /\d/.test(p) },
  { id: "special", test: (p: string) => /[^A-Za-z0-9\s]/.test(p) },
] as const;

export function passwordChecks(p: string) {
  return PASSWORD_RULES.map((r) => r.test(p));
}
