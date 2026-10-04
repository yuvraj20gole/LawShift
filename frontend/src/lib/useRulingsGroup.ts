"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { API_BASE } from "./api";

export type ArchiveRow = {
  court: string;
  decidedOn: string;
  title?: string;
  caseType?: string;
  caseNumber?: string | null;
  bench?: string;
  benchLabel?: string | null;
  disposalOutcome?: string;
  branch: string;
  link: string;
  linkKind: "court" | "archive" | "other";
};

export type CourtMeta = {
  groupLabel?: string;
  newestRecordDate?: string;
  count?: number;
  sampleRule?: { perWeek: number; weeks: number };
};

export type BenchFacet = { code: string; benchLabel: string | null; count: number };

type Params = {
  court: string;
  branch?: string;
  q?: string;
  bench?: string | null;
  enabled: boolean;
};

const PAGE = 25;

/**
 * One court's archive rows from GET /api/rulings, 25 at a time. Changing any
 * filter starts again from the first page; `loadMore` appends the next page.
 */
export function useRulingsGroup({ court, branch, q, bench, enabled }: Params) {
  const [rows, setRows] = useState<ArchiveRow[]>([]);
  const [total, setTotal] = useState(0);
  const [meta, setMeta] = useState<CourtMeta | null>(null);
  const [benches, setBenches] = useState<BenchFacet[]>([]);
  const [status, setStatus] = useState<"idle" | "loading" | "ok" | "failed">("idle");
  const seq = useRef(0);

  const key = [court, branch ?? "", q ?? "", bench ?? "", enabled].join("|");

  const fetchPage = useCallback(
    async (offset: number, append: boolean) => {
      const mine = ++seq.current;
      setStatus("loading");
      const p = new URLSearchParams({ court, limit: String(PAGE), offset: String(offset) });
      if (branch) p.set("branch", branch);
      if (q) p.set("q", q);
      if (bench) p.set("bench", bench);
      try {
        const r = await fetch(`${API_BASE}/api/rulings?${p.toString()}`);
        if (!r.ok) throw new Error(String(r.status));
        const d = await r.json();
        if (mine !== seq.current) return;
        const got: ArchiveRow[] = Array.isArray(d.rulings) ? d.rulings : [];
        setRows((prev) => (append ? [...prev, ...got] : got));
        setTotal(d.totalMatching ?? got.length);
        setBenches(Array.isArray(d.benches) ? d.benches : []);
        const courts = d.courts ?? {};
        const name = Object.keys(courts).find((k) => k.toLowerCase().includes(court.toLowerCase()));
        setMeta(name ? courts[name] : null);
        setStatus("ok");
      } catch {
        if (mine === seq.current) setStatus("failed");
      }
    },
    [court, branch, q, bench],
  );

  useEffect(() => {
    if (!enabled) {
      seq.current++;
      setRows([]);
      setTotal(0);
      setStatus("idle");
      return;
    }
    void fetchPage(0, false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  const loadMore = useCallback(() => void fetchPage(rows.length, true), [fetchPage, rows.length]);

  return { rows, total, meta, benches, status, loadMore, hasMore: rows.length < total };
}
