# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Next.js (App Router) + TypeScript + CSS Modules. Confirmed by proceeding after unanswered stack decision page (recommended option); change on request.

## Users

Primary: Indian law students, junior advocates, and journalists who need to know whether a fact pattern is governed by IPC or BNS after the 1 July 2024 transition, without inventing citations. [INFERRED from brief + PROCESS_LOG architecture]

Secondary: researchers evaluating temporal legal-RAG systems. [INFERRED]

## Product Purpose

LawShift maps a user’s case description (chat or uploaded document) to the correct Indian criminal statute under the 2024 IPC→BNS transition, then produces a grounded IRAC answer from retrieved statutory text, with visible pipeline steps and optional Hindi/Marathi translation.

Success: the visitor understands the deterministic gate in under two seconds, trusts evaluation numbers that come from held-out runs, and enters the real chat product.

## Positioning

Article 20(1) routing is a hard date rule (pre/post 1 July 2024), not a model guess; retrieval is act-aware cascade with bifurcation when scores are close; generation is constrained to retrieved text and Rule-only verified. A generic chatbot cannot truthfully claim the same.

## Operating Context

FastAPI pipeline Stages 0–5 (`app/`): document OCR → date extract → deterministic gate → act-aware cascade retrieve → IRAC synthesize + Rule-only verify → optional IndicTrans2/Ollama translation. Evidence and process history live in `PROCESS_LOG.md` and `results/`.

## Capabilities and Constraints

- Chat query and document upload (typed PDF, scanned PDF OCR, JPEG/PNG)
- Bifurcation disambiguation when multiple sections score within margin
- Languages: EN (default), HI, MR for IRAC output only
- 5 free questions without sign-up (product claim from brief; auth UI present as Login/Sign Up, backend auth not yet confirmed)
- Not legal advice — informational tool only
- Open: About page content depth; auth provider; production API URL [UNDECIDED]

## Brand Commitments

- Name: **LawShift**
- Visual register (binding from brief): serious fintech / legal-research product — Stripe, Linear, Bloomberg Law microsite energy. Professional Dark / Minimal Light two-theme system. Restrained slate/navy, one accent used sparingly, never neon or glow.
- Explicit bans from brief: purple-to-blue gradient blobs, floating 3D orbs, rounded-icon feature grids, fake testimonials, stock AI/scales clip art, emoji decoration, gradient text/buttons, glow/shadow card effects, Inter-as-everywhere default
- Typography direction (binding): strong serif/slab for hero + statutory excerpts; clean grotesque sans for UI/body (e.g. Source Serif 4 + Manrope — Inter avoided per craft floor)
- Interactive hero date widget must be real (client-side cutoff vs 2024-07-01), not a mock screenshot
- Trust stats, comparison table, how-it-works diagram must use real project content

## Evidence on Hand

- Routing accuracy 100% by construction (Stage 2 deterministic gate) — PROCESS_LOG §14 / e2e
- Retrieval Recall@5 **0.841** (held-out test, `results/final_selected_model_test_eval.json`)
- Zero fabricated citations across 40 Stage 4 generations (PROCESS_LOG §16)
- Datasets/models: GSMS-B, nandhakumarg IPC↔BNS mapping, GovIntel, nyaya-eval-v0, AI4Bharat IndicTrans2
- Do not invent testimonials, customer logos, or unmeasured benchmarks

## Product Principles

1. Visible-not-silent: pipeline steps, OCR tagging, bifurcation prompts — never hide mechanism.
2. Hard rules where Article 20(1) requires them; models only where generation needs them.
3. Every marketing number must trace to a results file or process-log section.
4. Informational tool, not legal advice — disclaimer always present.
5. Content does the work; decoration that is not product truth does not ship.

## Accessibility & Inclusion

Keyboard-reachable theme/language toggles and accordion FAQ; sufficient contrast in both themes; responsive down to 375px. [INFERRED minimum from brief]
