# LawShift: working notes for Claude Code

Detail lives in `PROCESS_LOG.md` (sections 1-28) and `DESIGN.md`. This file is the quick start.

## 1. What LawShift is

LawShift helps law students, junior advocates and journalists find out whether the Indian Penal Code (IPC) or the Bharatiya Nyaya Sanhita (BNS) applies to an offence, then shows the section text as stored, with a one-sentence-per-field IRAC answer and a "worth double-checking" flag. It is an informational research tool, not legal advice.

**The rule that drives it:** the offence date decides the substantive code. Before 1 July 2024 is IPC; on or after it is BNS. This is a hard date comparison in code (`app/stage2.py`), never a model decision.

## 2. RULES for working in this repo

- **No git writes.** Never run `git add`, `commit`, `push`, `stash`, `rebase`, `reset`, or anything that changes history or the index. Never add a Co-authored-by line. Reading commands (`status`, `log`, `diff`) are fine. The owner commits and pushes from a plain Terminal. (Also in `.cursor/rules/no-git.mdc`.)
- **Measure before changing the pipeline.** Do not change retrieval, the bifurcation margin (0.10), the Stage 4 prompts, the verifier or the models without measuring against the regression suite (section 8) first.
- **Never invent** data, cases, judgments or holdings. Anything unverified is `verified:false` or "to verify". Sample data is labelled as sample data.
- **Statute text is shown as stored.** It has digitisation slips; do not "fix" it in `data/clean/`.
- **Hindi and Marathi strings written by AI are drafts** that need native review. Keep them listed (section 10).
- **Design:** follow `DESIGN.md` (Bare Act system). No stock images, no stat tiles, no gradients, no icon circles. Every claim scoped or sourced; verification states always icon + words.
- **Tool split so far:** Cursor for backend, data and diagnosis work; Claude Code for design and structural UI work. Prompts for either tool must never include commit or push steps.
- **Public repo.** No tokens, keys, personal data, or real party names from any case in any committed file.

## 3. How to run it

Three things must be running: Ollama (both models), the backend on 8000, the frontend on 3000.

```
ollama serve                                   # native arm64 build
ollama pull qwen2.5:3b-instruct                # writer
ollama pull qwen2.5:14b-instruct               # verifier
# backend (repo root)
.venv/bin/uvicorn app.main:app --reload --port 8000
# frontend
cd frontend && npm run dev                     # next dev --turbopack, port 3000
```

Frontend calls `http://127.0.0.1:8000` (`frontend/src/lib/api.ts`, override with `NEXT_PUBLIC_API_BASE`); `next.config.ts` also rewrites `/api/*` to 8000.

**Cold-start checklist (after a restart):**
1. Ollama is the native **arm64** build and runs on the GPU: `ollama ps` shows `100% GPU`. The Intel build under Rosetta ran on CPU and was about 20 times slower (PROCESS_LOG section 20).
2. `transformers` stays at **4.44.2** (`.venv/bin/python -c "import transformers"`; this is what the venv has now). `app/stage5_translate.py` carries a shim in case it is ever upgraded.
3. `HUGGINGFACE_HUB_TOKEN` is in the shell that starts uvicorn (IndicTrans2 is a gated model). Never write the token into a file.
4. `LAWSHIFT_FORCE_OLLAMA_TRANSLATE=0` (the default) uses the real IndicTrans2; `=1` forces the Ollama fallback, which gave wrong dates and subjects in Hindi/Marathi.
5. `models/finetuned-bge-small-ipc-bns-e8` exists (gitignored, see section 7).
6. Startup logs `[startup] Ready.` after Stage 3 loads and both Ollama models are warmed (about 11 s).
7. Stale frontend bundle? Kill `next dev`, `rm -rf frontend/.next`, restart.

Earlier ML runs also set `TRANSFORMERS_NO_TF=1 TRANSFORMERS_NO_FLAX=1 USE_TF=0 TOKENIZERS_PARALLELISM=false TORCHDYNAMO_DISABLE=1` (system TensorFlow aborts on that CPU).

## 4. Pipeline (order a message passes through; code in `app/main.py`, `handle_query`)

- **Stage 1: date extraction** (`app/stage1.py`, wraps `src/stage1_entity_extraction.py`). Rule-based, no LLM. Does not parse ISO dates (2024-07-01), so the chat asks for the date instead. Rejects ambiguous numeric dates; keyword-context scoring for multi-date text.
- **Date lock per conversation** (`_LOCKED_DATES`, in server memory, lost on restart). First resolved date wins. **Date-conflict rule:** a later different date on the same side of 1 July 2024 keeps the lock and adds a one-line note; on the opposite side it returns a `bifurcation` with `reason=date_conflict` (two dates as options), no retrieval; choosing one replaces the lock and re-runs the held message.
- **Stage 2 gate** (`app/stage2.py`): `< 2024-07-01` is IPC, else BNS; no date gives a `clarify`.
- **Missing-facts gate:** after Stage 2, before retrieval. Strips the date, drops stopwords and `MISSING_FACTS_META_WORDS` (word list constant in `app/main.py`) and pure digits; if no content word is left, `clarify` with `reason=missing_facts`. Explicit section citations pass through (`EXPLICIT_CITATION_RE`).
- **Code-mismatch rule:** an explicit IPC or BNS citation that disagrees with the date's code is intercepted before Stage 3 and looked up in the mapping table; equivalents are offered as a `bifurcation` (`reason=code_mismatch`), none gives a `clarify`. BNSS/BSA/CrPC and bare numbers are not intercepted.
- **`section_lookup`:** a citation-only message (no facts) whose code matches the route skips retrieval and writing and returns up to three cards (code, section, heading, text as stored, mapping line). No IRAC; the counter does not decrement.
- **Stage 3** (`app/stage3.py`): act-aware cascade (exact section match plus dense retrieval, fine-tuned `bge-small-en-v1.5` e8, k=5). **Bifurcation:** `detect_bifurcation(margin=0.10)` looks at the next 3 scores. Every bifurcation ends with the option "None of these. I will describe what happened"; choosing it returns `clarify` (`reason=describe_facts`). Rejected options are remembered per conversation (`_REJECTED_BIFURCATION_SECTIONS`): if a later set is entirely rejected, cards are returned instead of asking again. A message that already cites an in-force section of the routed code plus facts skips bifurcation and answers under the cited section (an `info_note` if the section is missing).
- **Stage 4 writer** (`src/stage4_generate.py`, wrapped by `app/stage4.py`): `qwen2.5:3b-instruct`, temperature 0.1, **no seed** (so runs are not reproducible). A v2 prompt exists behind `STAGE4_PROMPT_VERSION=v2` and is **not** the default (PROCESS_LOG section 26).
- **Stage 4 verifier:** `qwen2.5:14b-instruct`, rule-only v3 prompt (`src/stage4_verify_ruleonly_14b_v2.py`), sees only the generated Rule and Conclusion. It produces a soft "worth double-checking" flag, never a hard block.
- **Stage 5 translation** (`app/stage5_translate.py`): IndicTrans2 for HI/MR after Stages 1-4, batched; language never changes routing, retrieval or verification.
- **Document upload** (`app/stage0_document.py`): `pdfplumber` text, Tesseract OCR fallback for scanned PDFs; extracted text then goes through the same pipeline. Date-only extracts give `missing_facts`.
- **Display lines (frontend):** "Offence date used" (from `offense_date_used`: label, code, source), the Exception/Explanation/Proviso notice (when the source text matches), the scope line after verification, and the `[Context: ...` prefix stripped from displayed statute text.

## 5. API routes (all in `app/main.py`; CORS open)

- `POST /api/query` (`QueryRequest`: message, `conversation_id`, `language`) returns one of `mapping` (IRAC, sources, verification, pipeline steps), `clarify` (reasons include missing_facts, code_mismatch, describe_facts), `bifurcation` (options; reasons score_gap, code_mismatch, date_conflict), `section_lookup` (cards; reasons citation_only, bifurcation_exhausted), `failure` (no_mapping, ambiguous, source_unavailable). Schemas in `app/schemas.py`.
- `POST /api/query/resolve_bifurcation` takes the chosen option. For score-gap it skips retrieval and runs Stage 4 on the chosen chunk; for date_conflict it replaces the lock and re-runs.
- `POST /api/upload_document` returns the same response kinds from an uploaded PDF/image.
- `GET /api/map?code=IPC|BNS&section=` is a read-only lookup over `mapping.jsonl` plus statute text, no model calls (`app/mapping_lookup.py`). `GET /api/map/sections?code=` gives numbers and titles for suggestions.
- `GET /api/rulings` reads `data/rulings_index.json`: filters `court`, `branch`, `q`, `bench`; paging `limit`, `offset`; newest first; returns `totalMatching` and a bench facet.
- `GET /health` returns status plus counts of locked conversations and pending bifurcations.

## 6. Frontend map (`frontend/`, Next.js App Router, CSS Modules)

- `/` landing: hero, embedded `ChatEntry`, comparison cards, "Where it stops" band, FAQ. `/about` has the raw metrics.
- `/login`, `/register`, `/forgot-password`: **UI only**, nothing is sent or saved, a "Preview" note says so.
- `/dashboard` redirects to `/dashboard/workspace`. Pages: Workspace (real chat, `ChatEntry hideCounter hideExamples unlimited`), Mapping (real data), Case history, Documents, Rulings (real data), Settings.
- **Sample data + "Preview" strip:** Case history, Documents, Settings (and Workspace's attach control is a stub). The strip is hidden on Mapping and Rulings (`DashboardShell.tsx`).
- `ChatEntry` props: `hideCounter`, `hideExamples`, `initialDraft` (prefill from Mapping's "Ask in Workspace" via sessionStorage), `unlimited`. The counter starts at 5 and decrements **only on `kind === "mapping"` answers**; the 5-question limit applies to anonymous landing-page visitors only (dashboard passes `unlimited`).
- Shared: `components/CodeCompare.tsx` (landing and Mapping), `lib/wordDiff.ts`, `lib/useRulingsGroup.ts`, `components/dashboard/BenchTip.tsx`.
- i18n (EN/HI/MR): `lib/landingCopy.ts`, `lib/dashboardCopy.ts`, `lib/authCopy.ts`, `lib/i18n.ts` (chat and static page dictionary).
- Unused leftovers: `components/dashboard/ComingNext.tsx`, `lib/useLatestRulings.ts`, old keys `mapWill`, `rulWill`, `soon*` in `dashboardCopy.ts`. `frontend/_archive/` is old work; do not copy from it.

## 7. Data

- `data/clean/mapping.jsonl`: 562 IPC-BNS rows (section 294, partial 122, merged 117, dropped 29). `data/clean/statutes.jsonl`: 1059 BNS/BNSS/BSA sections (each text carries a `[Context:...]` prefix). `data/clean/ipc_statutes.jsonl`: 562 IPC sections built from the mapping.
- `data/rulings_index.json`: built by `scripts/build_rulings_index.py` from the open AWS archives (anonymous S3, CC BY 4.0, Dattam Labs). Supreme Court: 200 most recent records. Bombay High Court: a weekly sample (60 per week over 26 weeks, bench labels only from PDF headers). The archive lags the courts and its dates can be wrong. Index rows have no `topic` field, so the "IPC & BNS" chip only matches curated entries.
- `frontend/src/data/rulings.ts`: curated Featured and Background entries. All `verified:false` until a human has read the judgment. `HIDE_UNVERIFIED` is `false` and must be `true` before launch. Fields saying "to verify" currently: one Background entry's `decidedOn`.
- `models/` is gitignored (about 1.3 GB). A fresh clone cannot run retrieval without it.

## 8. Regression suite

Any pipeline change is checked against these, with numbers. The harnesses were written under `/tmp` (`/tmp/lawshift_*.py`), not in the repo, and may be gone after a restart (rewrite them if needed); only the Stage 1 and Stage 3 data files are in the repo.

| Check | Expected | Where |
|---|---|---|
| Nine diagnosis queries (fact-free: clarify; with facts: unchanged) | 9/9 | `/tmp` (script not in repo) |
| About 30 fact-free variants | 27 blocked, 3 not (ISO dates, no date parsed) | `/tmp` |
| False-block test, 285 questions + a date | 0 blocked | `/tmp` |
| Stage 1 (30 real + 14 stress) | 44/44 | `results/stage1_real_eval.json`, `stage1_stress_test.json`, `stage1_v2_eval.json` |
| Stage 3 Recall@5 on test (n=636) | 0.841 (535/636) | `results/final_selected_model_test_eval.json`; harness `src/final_retrieval_test.py` |
| 85-question bifurcation count at margin 0.10 | 47 (46 with comma-appended date, a punctuation artifact) | `/tmp/lawshift_bif85_recount.py` |
| Six code-mismatch cases | 6/6 | `/tmp` |
| Seven section_lookup cases | 7/7 | `/tmp` |
| Date-conflict cases | all pass | `/tmp` |
| Stubbed counter 5, 5, 5, 5, 4 | exact | `/tmp` |

## 9. Known issues and limits

- The writer's Application and Conclusion can assert facts the user did not give and sometimes say "is guilty" or "should be punished". The checker only sees Rule and Conclusion, so it cannot see what the Rule left out, and its verdict on identical input can differ between runs.
- Translation can change how firm a sentence is (shall, may, would).
- Fresh writer runs do not reproduce the stored 40 outputs (temperature 0.1, no seed); "0 of 40 fabricated" was a hand review.
- Stage 1 does not parse ISO dates; the chat asks for the date.
- Bifurcation fires often (47 of 85 plain questions).
- Date locks, pending bifurcations and rejected options live in server memory and are lost on restart.
- Auth is UI only and `/dashboard` is open to anyone. Do not deploy before real auth.
- The 3B model unloads after about 5 idle minutes (no `keep_alive` is set for it); the 14B and translation calls set `keep_alive: 30m`. The keep-alive check has not reported back (unverified).
- LawShift picks the substantive code from the offence date and does not model procedure; High Courts have reached different results on which procedural code applies to older offences.
- Mapping table is community-maintained; check the official text.

## 10. Open work, in planned order

1. **Pending decision from the owner:** keep the generated Conclusion (Option A), or replace it with a fixed sentence the code writes (Option B: "On the facts described, this appears to fall within <code> <section> (<heading>)"). If B, re-measure against section 8 and note it for the paper.
2. Keep-alive check for both Ollama models.
3. Landing copy pass (Claude Code): docket card says "BNS 178, 179 or 180" (`components/Docket.tsx`) but the pipeline offers 180 and 179; chat legend wording; a row for "you give a date but no facts"; "where it stops" lines about the checker's blind spot and translation changing firmness; licence names (CC BY 4.0, CC BY-NC 4.0) beside GovIntel and nyaya-eval-v0 in the footer. (The "Procedure can follow a different date" row is done.)
4. Owner checks: Mapping and Rulings in HI and MR; read the featured Supreme Court judgments before setting `verified:true`; the Marathi flow from a fresh page.
5. Cleanups: move three procedural Bombay outcomes to `BOMBAY_OUTCOMES_EXCLUDED` (which three: unverified); delete unused `ComingNext.tsx`, old copy keys and `useLatestRulings.ts`; exclude `frontend/_archive` from the type-check; a README on obtaining `models/`.
6. Functionality phase: make the Workspace attach control real (upload, extract, confirm the date, lock it, follow-ups); Supabase auth; Supabase data (settings, history and stars, document storage and picker, privacy wording); a rate limit; native HI/MR review of every AI-written string, collected in one document; deployment last.

**AI-drafted HI/MR strings awaiting native review:** all HI/MR text in `landingCopy.ts`, `dashboardCopy.ts`, `authCopy.ts`; chat fallbacks in `i18n.ts` (clarify, mismatch, `sectionLookupExhaustedNote`, `sectionMissingSearchNote`, `mappingPhraseMerged`, offence-date lines, scope line, language-switch note). Curated ruling titles and holdings are English only.

## 11. Files to read first

`CLAUDE.md`, `DESIGN.md`, `PRODUCT.md`, `PROCESS_LOG.md` (sections 18-28 for the live pipeline), `app/main.py` (`handle_query`, `resolve_bifurcation`), `app/schemas.py`, `app/stage3.py`, `src/stage4_generate.py`, `frontend/src/components/ChatEntry.tsx`, `frontend/src/lib/dashboardCopy.ts`, `frontend/src/data/rulings.ts`, `scripts/build_rulings_index.py`.
