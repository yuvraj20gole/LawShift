# Landing attempt v1 — split-reveal dark (+ light preview)

Archived so a fresh landing redesign does not inherit these visual choices.
**Do not import from this folder into the live app.**

## What this was
- Split-reveal IPC/BNS hero from real statute JSONL backdrop
- Tinted near-black section surfaces + temporary `?preview=light` warm paper palette
- Plain-language trust cards, comparison table, how-it-works, FAQ, footer
- Earlier experiments still in this tree: date-gate widget, era timeline,
  product preview, CTA band

## Intentionally NOT archived (live product)
- `src/components/ChatEntry.*` — working “Ask a case question” workspace
- `src/components/Header.*` — site chrome
- `src/components/Reveal.tsx` + `src/hooks/useReveal.ts` — used by ChatEntry
- Backend / API / Stage 1–4 pipeline

## How to view historically
Open the copied `app/page.tsx` and `components/*` as reference only.
Restore would require manually moving files back into `src/` and wiring imports.
