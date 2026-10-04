"use client";

import { useEffect, useState } from "react";
import { BACKGROUND_RULINGS, type RulingEntry } from "@/data/rulings";

/** Same base the chat uses: the FastAPI service, called directly. */
const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") || "http://127.0.0.1:8000";

const COURT = "Supreme Court of India";

/** One row of GET /api/rulings (fields as in data/rulings_index.json). */
export type ArchiveRuling = {
  court: string;
  decidedOn: string;
  title: string;
  caseType?: string;
  branch?: string;
  link: string;
  linkKind: "court" | "archive";
};

export type RulingsState =
  | { status: "loading" }
  | { status: "ok"; rulings: ArchiveRuling[]; newestRecordDate: string | null }
  | { status: "failed"; fallback: RulingEntry[] };

/** The three newest Supreme Court entries from the read-only archive route. */
export function useLatestRulings(limit = 3): RulingsState {
  const [state, setState] = useState<RulingsState>({ status: "loading" });

  useEffect(() => {
    let alive = true;
    const url = `${API_BASE}/api/rulings?court=${encodeURIComponent(COURT)}&limit=${limit}`;
    fetch(url)
      .then((r) => {
        if (!r.ok) throw new Error(String(r.status));
        return r.json();
      })
      .then((d) => {
        if (!alive) return;
        const rows: ArchiveRuling[] = Array.isArray(d?.rulings) ? d.rulings : [];
        if (rows.length === 0) throw new Error("empty");
        const newest: string | null = d?.courts?.[COURT]?.newestRecordDate ?? null;
        setState({ status: "ok", rulings: rows, newestRecordDate: newest });
      })
      .catch(() => {
        if (alive) setState({ status: "failed", fallback: BACKGROUND_RULINGS });
      });
    return () => {
      alive = false;
    };
  }, [limit]);

  return state;
}
