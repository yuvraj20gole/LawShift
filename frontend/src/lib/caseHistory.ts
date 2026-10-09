import { createClient } from "@/lib/supabase/client";

export type HistoryCode = "IPC" | "BNS" | "BNSS" | "BSA";

export type CaseRow = {
  id: string;
  created_at: string;
  question: string;
  offence_date: string | null;
  code: HistoryCode;
  section: string;
  heading: string | null;
  flagged: boolean;
  starred: boolean;
  language: "en" | "hi" | "mr";
};

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

/** "25 June 2024" (the API's English label) -> "2024-06-25"; anything else -> null. */
export function labelToIso(label: string | undefined | null): string | null {
  const m = /^\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\s*$/.exec(label ?? "");
  if (!m) return null;
  const mi = MONTHS.findIndex((n) => n.toLowerCase() === m[2].toLowerCase());
  if (mi < 0) return null;
  const d = new Date(Date.UTC(+m[3], mi, +m[1]));
  if (d.getUTCMonth() !== mi || d.getUTCDate() !== +m[1]) return null;
  return `${m[3]}-${String(mi + 1).padStart(2, "0")}-${String(+m[1]).padStart(2, "0")}`;
}

/** "2024-09-05" -> "5 September 2024". */
export function isoToLong(iso: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  if (!m) return iso;
  return `${+m[3]} ${MONTHS[+m[2] - 1]} ${m[1]}`;
}

/** The question as the Workspace starting text, with the saved offence date appended when the text lacks it. */
export function openingText(question: string, offenceDate: string | null): string {
  if (!offenceDate) return question;
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(offenceDate);
  if (!m) return question;
  const day = String(+m[3]);
  const month = MONTHS[+m[2] - 1];
  const year = m[1];
  const hay = question.toLowerCase();
  const found =
    new RegExp(`\\b0?${day}(st|nd|rd|th)?\\s+(of\\s+)?${month}\\b,?\\s+${year}`, "i").test(hay) ||
    new RegExp(`\\b${month}\\s+0?${day}(st|nd|rd|th)?,?\\s+${year}`, "i").test(hay) ||
    hay.includes(offenceDate);
  return found ? question : `${question.replace(/[.,\s]+$/, "")}, ${day} ${month} ${year}`;
}

/** The most a stored answer may weigh (the database allows 120000 bytes; this leaves headroom). */
export const RESULT_MAX_BYTES = 110000;

/** The answer as JSON text if it is small enough to store, else null (the row is then saved without it). */
function storableResult(result: unknown): unknown | null {
  try {
    if (result === undefined || result === null) return null;
    const json = JSON.stringify(result);
    if (new TextEncoder().encode(json).length > RESULT_MAX_BYTES) return null;
    return JSON.parse(json);
  } catch {
    return null;
  }
}

/**
 * Saves one mapped answer for a logged-in user: the metadata, plus the finished answer card as `result`
 * when it fits. Fire and forget: every failure is swallowed, and only a generic message is logged.
 * If the insert is refused with the answer attached, it is tried once more without it.
 */
export async function saveCase(row: {
  question: string;
  offence_date: string | null;
  code: string;
  section: string;
  heading: string | null;
  flagged: boolean;
  language: string;
  result?: unknown;
}): Promise<void> {
  try {
    const supabase = createClient();
    const { data } = await supabase.auth.getSession();
    if (!data.session) return; // anonymous visitors: nothing is saved
    if (!["IPC", "BNS", "BNSS", "BSA"].includes(row.code)) return;
    if (!["en", "hi", "mr"].includes(row.language)) return;
    const question = row.question.trim().slice(0, 4000);
    if (!question || !row.section) return;
    const base = {
      question,
      offence_date: row.offence_date,
      code: row.code,
      section: row.section.slice(0, 20),
      heading: row.heading ? row.heading.slice(0, 300) : null,
      flagged: row.flagged,
      language: row.language,
    };
    const result = storableResult(row.result);
    const payload: Record<string, unknown> = result ? { ...base, result } : base;
    let { error } = await supabase.from("case_history").insert(payload);
    if (error && result) ({ error } = await supabase.from("case_history").insert(base));
    if (error) console.warn("History save failed");
  } catch {
    console.warn("History save failed");
  }
}

/** One saved row's question, language, date and stored answer (read only when History "Open" needs it). */
export type SavedAnswerRow = { question: string; language: "en" | "hi" | "mr"; created_at: string; result: unknown };

export async function loadSavedAnswer(id: string): Promise<SavedAnswerRow | null> {
  try {
    const { data, error } = await createClient()
      .from("case_history")
      .select("question,language,created_at,result")
      .eq("id", id)
      .maybeSingle();
    if (error || !data) return null;
    const lang = data.language === "hi" || data.language === "mr" ? data.language : "en";
    return { question: String(data.question ?? ""), language: lang, created_at: String(data.created_at ?? ""), result: data.result ?? null };
  } catch {
    return null;
  }
}
