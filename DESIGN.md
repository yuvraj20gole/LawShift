# Design system

Replaces the earlier dark amber/teal system (archived under `frontend/_archive/`). Derived from the shipped build (landing, About, sign-in screens).

## World

A Bare Act page. Light, because statute text is read at a desk in daylight. Section headings sit in a left margin like marginal notes; each section's lead line is centred above its grid. Evidence is shown as ruled rows and labelled charts, never as feature cards. One navy band (the chat) and a navy hero panel and footer give the page its rhythm.

## Color (live tokens in `frontend/src/app/globals.css`)

| Token | Value | Meaning |
|---|---|---|
| `--paper` / `--paper-dim` / `--sunken` | `#F8FAFC` / `#EFF3F8` / `#E6EBF3` | Page grounds |
| `--surface` | `#FFFFFF` | Cards, chat panel, form card |
| `--ink` / `-secondary` / `-tertiary` | `#0F172A` / `#475569` / `#566377` | Text |
| `--rule` / `--rule-strong` | `#D5DDE8` / `#A3AFC0` | Hairlines, input borders |
| `--bns` | `#1E3A8A` | The new code (BNS), primary actions, links |
| `--ipc` | `#475569` | The old code (IPC) |
| `--cutoff` | `#B45309` | 1 July 2024, section rules, "preview" notes |
| `--flag` / `--flag-wash` | `#B91C1C` / `#FDECEB` | "Worth double-checking" and every error |
| `--ok` / `--ok-wash` | `#166534` / `#E4F3EA` | "No inconsistency detected" and every all-clear |
| `--night` | `#0B1630` | Chat band, hero panel, footer, auth panel |

One meaning per colour. No gradients, glows or grain. (`--seam` no longer exists: it split into `--flag` and `--cutoff`.)

## Typography

- **Serif (display, statute text, headings):** Literata (optical size on). Devanagari falls back to Noto Serif Devanagari.
- **Sans (UI, body):** Public Sans. Devanagari falls back to Noto Sans Devanagari.
- Font variables are declared on `body`, because `next/font` defines them there.
- Root font size stays 16px; the container widens (to 1400px) instead of the text growing.

## Sign-in screens (`/login`, `/register`, `/forgot-password`)

- Navy panel (hero line + the bronze 1 July 2024 rule) beside a white form card with a bronze rule above the title.
- Errors reuse the "Worth double-checking" treatment: `--flag-wash` strip, `--flag` text, flag icon. All-clear ("Passwords match") reuses "No inconsistency detected".
- Register shows a live five-rule password checklist (hollow box → `--ok` filled check); submit stays disabled until email, all five rules and the confirmation are valid.
- Login accepts any password and only validates email shape and non-empty fields.
- Submit shows a spinner and disables; success is a placeholder panel with a bronze progress rule. A bronze "Preview" note states that nothing is sent or saved until the backend is wired.

## Motion

Authored moments: hero words rise and the navy panel settles on load; the chat band opens like a curtain; the step rail is drawn by scroll position; charts fill and numbers count up once in view; comparison cards arrive from their own sides. Smooth inertial scrolling via Lenis. Press feedback `scale(0.97–0.98)`, 140–160ms, ease-out; hover gated behind `(hover: hover) and (pointer: fine)`. Reduced motion removes all of it.

## Content rules

Every figure on the landing page carries its scope on the page. No overall accuracy figure. No clean-BNS (n=7) result. No ILDC claims. Raw metrics (Recall@5, MRR, NDCG) live on `/about`. Auth screens must not promise account features that do not exist.
