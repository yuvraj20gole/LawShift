# Design system

Replaces the earlier dark amber/teal system (archived under `frontend/_archive/`). Derived from the shipped landing build.

## World

A Bare Act page. Light, because statute text is read at a desk in daylight. Each section's heading sits in a left margin like a marginal note, with the argument beside it. Evidence is shown as ruled tables and definition lists, never as cards or metric tiles.

## Color

| Token | Value | Role |
|---|---|---|
| `--paper` | `#F3F4F0` | Page ground (cool bone, not cream) |
| `--surface` | `#FBFBF8` | Chat shell, docket cases, aside |
| `--sunken` | `#EAECE6` | Chat band ground |
| `--ink` / `-secondary` / `-tertiary` | `#12161F` / `#424957` / `#636A78` | Text |
| `--rule` / `--rule-strong` | `#D2D5CD` / `#AEB3A9` | Hairlines |
| `--bns` | `#22318A` | New code, primary actions, links on hover |
| `--ipc` | `#4A5566` | Old code |
| `--seam` | `#B3261E` | 1 July 2024, and "Worth double-checking" flags |
| `--ok` | `#2C654A` | "No inconsistency detected" |

One meaning per colour. No gradients, glows or grain.

## Typography

- **Serif (display, statute text, section headings):** Literata, optical size axis on. Devanagari falls back to Noto Serif Devanagari.
- **Sans (UI, body):** Public Sans. Devanagari falls back to Noto Sans Devanagari.
- Font variables are declared on `body`, because `next/font` defines them there.
- Hero: `clamp(2.5rem, 6.4vw, 5rem)`, weight 450, tracking -0.03em. Section lead lines are serif at `clamp(1.4rem, 2.5vw, 1.85rem)`.

## Layout

- Container 1160px. Sections use a 14rem margin column plus body (collapses under 900px).
- Hero is a statement, then the docket: three recorded cases placed left or right of a red 1 July 2024 seam by date.
- The real chat (`ChatEntry`) sits in the second band. IRAC fields in answers use the same margin-label pattern.

## Motion

One authored moment: on load the seam is drawn, then each docket case settles into its side. Everything else is press feedback (`scale(0.97)`), 140–160ms, ease-out. Hover is gated behind `(hover: hover) and (pointer: fine)`. Reduced motion removes all animation.

## Content rules

Every figure on the landing page carries its scope on the page. No overall accuracy figure. No clean-BNS (n=7) result. No ILDC claims. Raw metrics (Recall@5, MRR, NDCG) live on `/about`.
