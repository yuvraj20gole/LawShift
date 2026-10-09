# LawShift: working notes for Claude Code

Detail lives in `PROCESS_LOG.md` (sections 1-32) and `DESIGN.md`. This file is the quick start. Where this file and the repo disagree, trust the repo and fix this file.

## 1. What LawShift is, and where it stands

LawShift helps law students, junior advocates and journalists find out whether the Indian Penal Code (IPC) or the Bharatiya Nyaya Sanhita (BNS) applies to an offence, then shows the section text as stored, with a one-sentence-per-field IRAC answer and a "worth double-checking" flag. It is an informational research tool, not legal advice.

**The rule that drives it:** the offence date decides the substantive code. Before 1 July 2024 is IPC; on or after it is BNS. This is a hard date comparison in code (`app/stage2.py`), never a model decision.

**State:** `main` is at the `demo-v2` tag (commit 9257433). `demo-v1` is the earlier safe build from before accounts. `feature/accounts` points at the same commit as `main`, so it was merged (checked from `.git/refs`, not with git). Working tree state is the owner's to check.

## 2. RULES for working in this repo

- **No git writes.** Never run `git add`, `commit`, `push`, `stash`, `rebase` or `reset`, or anything that changes history or the index. Never add a Co-authored-by line. Some prompts also forbid reading git; follow the prompt. The owner commits and pushes from a plain Terminal. Prompts for any tool must never include commit or push steps.
- **Measure before changing the pipeline.** Do not change retrieval, the bifurcation margin (0.10), the Stage 4 prompts, the verifier or the models without running the regression suite (section 8) first.
- **Never invent** data, cases, judgments or holdings. Anything unverified is `verified:false` or "to verify". Sample data is labelled as sample data.
- **Statute text is shown as stored.** It has digitisation slips; do not "fix" it in `data/clean/`.
- **Hindi and Marathi strings written by AI are drafts** that need native review. Keep them listed (section 10).
- **Design:** follow `DESIGN.md` (Bare Act system). No stock images, stat tiles, gradients or icon circles. Every claim scoped or sourced; verification states always icon + words.
- **Public repo.** No tokens, keys, emails, personal data or real party names in any committed file. Never print a key. Only the publishable Supabase key is used in the frontend; never use a service-role or secret key.
- **Do not touch the other project** in `~/Downloads` (`Dependency_map`): it uses ports 5001 (unverified) and 3055 (seen running). Never kill processes by a broad pattern such as `next-server`; kill only this repo's PIDs.
- **Tool split:** Cursor for backend, data and diagnosis; Claude Code for design and structural UI work.

## 3. How to run it

Four things must be running: Ollama (both models), the backend on 8000, the frontend on **3000 only**. The backend CORS list and Supabase accept only `http://localhost:3000` (not `127.0.0.1:3000`).

```
ollama serve                                   # own terminal tab; native arm64 build
ollama pull qwen2.5:3b-instruct                # writer
ollama pull qwen2.5:14b-instruct               # verifier
# backend (repo root)
SUPABASE_URL=<project url> LAWSHIFT_ALLOWED_ORIGINS=http://localhost:3000 \
LAWSHIFT_ENABLE_DOCS=0 LAWSHIFT_TRUST_PROXY=0 \
.venv/bin/uvicorn app.main:app --reload --port 8000
# frontend
cd frontend && npm run dev                     # next dev --turbopack, port 3000
```

- The three `LAWSHIFT_*` values above are also the code defaults. `SUPABASE_URL` has a built-in default in `app/security_settings.py` (the project's public URL); set it explicitly anyway.
- `frontend/.env.local` (git-ignored) holds `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` (a publishable `sb_publishable_` key). `frontend/.env.local.example` has empty placeholders. If either is missing, auth cannot work.
- Frontend calls `http://127.0.0.1:8000` (`frontend/src/lib/api.ts`, override with `NEXT_PUBLIC_API_BASE`).
- Hugging Face (IndicTrans2 is gated): `app/stage5_translate.py` reads `HUGGINGFACE_HUB_TOKEN`/`HF_TOKEN` if set, else the cached `huggingface-cli` login. Never write a token into a file.
- `requirements-backend.txt` adds PyJWT and pytest/httpx. Install into the venv.

**Cold-start checklist:**
1. Ollama is the native **arm64** build on the GPU: `ollama ps` shows `100% GPU` (Intel/Rosetta was about 20 times slower, PROCESS_LOG section 20).
2. `transformers` stays at **4.44.2**; `app/stage5_translate.py` has a shim if upgraded.
3. `LAWSHIFT_FORCE_OLLAMA_TRANSLATE=0` (default) uses real IndicTrans2; `=1` gave wrong dates and subjects in Hindi/Marathi.
4. `models/finetuned-bge-small-ipc-bns-e8` exists (git-ignored, section 7).
5. Startup logs `[startup] Ready.` after Stage 3 loads and both models are warmed (about 11 s).
6. Stale frontend bundle? Kill this repo's `next dev`, `rm -rf frontend/.next`, restart. A `next build` also overwrites `.next`, so stop dev first.

Earlier ML runs also set `TRANSFORMERS_NO_TF=1 TRANSFORMERS_NO_FLAX=1 USE_TF=0 TOKENIZERS_PARALLELISM=false TORCHDYNAMO_DISABLE=1` (system TensorFlow aborts on that CPU).

**Speed and hosting:** on the Apple GPU an answer takes about 6 to 23 seconds. A CPU-only or free host is about 20 times slower or cannot hold the models. A rented 24 GB GPU is the proper deployment (check current prices; unverified).

## 4. Pipeline (code in `app/main.py`, `handle_query`)

- **Stage 1: date extraction** (`app/stage1.py`, wraps `src/stage1_entity_extraction.py`). Rule-based, no LLM. Does not parse ISO dates (2024-07-01); the chat asks for the date. Rejects ambiguous numeric dates.
- **Date lock per conversation** (`_LOCKED_DATES`, memory only). First resolved date wins. A later different date on the same side of 1 July 2024 keeps the lock with a one-line note; on the opposite side it returns a `bifurcation` with `reason=date_conflict`.
- **Stage 2 gate** (`app/stage2.py`): `< 2024-07-01` is IPC, else BNS; no date gives a `clarify`.
- **Missing-facts gate:** after Stage 2, before retrieval. If no content word is left once the date, stopwords and `MISSING_FACTS_META_WORDS` are removed, `clarify` with `reason=missing_facts`. Explicit section citations pass.
- **Code-mismatch rule:** an explicit IPC/BNS citation that disagrees with the date's code is looked up in the mapping table; equivalents become a `bifurcation` (`reason=code_mismatch`), none gives a `clarify`.
- **`section_lookup`:** a citation-only message whose code matches the route returns up to three cards, no IRAC, no quota use.
- **Stage 3** (`app/stage3.py`): act-aware cascade (exact section match plus dense retrieval, fine-tuned `bge-small-en-v1.5` e8, k=5). `detect_bifurcation(margin=0.10)`; every bifurcation ends with "None of these. I will describe what happened" (`clarify`, `reason=describe_facts`). Rejected options are remembered per conversation. A message citing an in-force section plus facts skips bifurcation.
- **Stage 4 writer** (`src/stage4_generate.py`, wrapped by `app/stage4.py`): `qwen2.5:3b-instruct`, temperature 0.1, no seed (runs are not reproducible), `keep_alive` 30m. Writes Issue, Rule and Application only. Prompt v2 exists behind `STAGE4_PROMPT_VERSION=v2`, not default.
- **Fixed Conclusion (Option B, implemented)**: with `LAWSHIFT_FIXED_CONCLUSION` (default 1) the Conclusion is a sentence written by code: "On the facts described, this appears to fall within <code> <section> (<heading>)." The response carries `fixed_conclusion`; the frontend renders a localised template for Hindi and Marathi (not translated). `=0` restores the generated Conclusion (PROCESS_LOG section 29).
- **Stage 4 verifier:** `qwen2.5:14b-instruct`, rule-only prompt (`src/stage4_verify_ruleonly_14b_v2.py`), `keep_alive` 30m. Sees only the Rule and the fixed Conclusion. Soft "worth double-checking" flag, never a block.
- **Stage 5 translation** (`app/stage5_translate.py`): IndicTrans2 for HI/MR after Stages 1-4. **Number guard** (`app/translation_number_guard.py`): if translation changes a number in a field, that field stays English, it is listed in `translation_fallback_fields`, and the chat shows a note. Number words ("two years") are not checked. Language never changes routing, retrieval or verification.
- **Document upload** (`app/stage0_document.py`): `pdfplumber` text, Tesseract OCR fallback. The route needs a login; the frontend does not call it yet (section 6).
- **Display lines (frontend):** "Offence date used", the Exception/Explanation/Proviso notice, the scope line, the `[Context: ...` prefix stripped, and a muted "Generated text..." line above the Application.

## 5. Backend API (`app/main.py`; hardening in PROCESS_LOG section 32)

- `POST /api/query` (`message`, `conversation_id`, `language`) returns `mapping`, `clarify`, `bifurcation`, `section_lookup` or `failure`. `POST /api/query/resolve_bifurcation` takes the chosen option. `POST /api/upload_document` returns the same kinds. Schemas in `app/schemas.py`.
- `GET /api/map?code=&section=` and `GET /api/map/sections?code=` read `mapping.jsonl` (no models). `GET /api/rulings` reads `data/rulings_index.json`. `GET /health` returns `{"status":"ok"}` only.
- **Auth** (`app/auth_supabase.py`): an optional Bearer token on query and resolve, required on upload. Verified against the project's JWKS (ES256), with an HS256 `SUPABASE_JWT_SECRET` fallback. A bad or expired token gives a clean 401. The pipeline works without a token.
- **Limits** (`app/limits.py`, `app/security_settings.py`): per-IP hourly caps on `/api/query` (12 anonymous, 120 logged in); a generation semaphore (default 2, 45 s wait, then 503 "busy"); uploads up to 10 MB with a PDF/JPEG/PNG type check; other bodies up to 100 KB. The client IP comes from `X-Forwarded-For` only when `LAWSHIFT_TRUST_PROXY=1`. Origins come from `LAWSHIFT_ALLOWED_ORIGINS`; `/docs` is off unless `LAWSHIFT_ENABLE_DOCS=1`.
- Date locks, pending bifurcations and rate-limit counters live in memory and reset on restart.

## 6. Frontend (`frontend/`, Next.js 15 App Router, CSS Modules)

- **Auth:** Supabase email + password via `@supabase/ssr` (cookie sessions). `src/middleware.ts` refreshes the session with `getClaims()`, sends signed-out `/dashboard/**` to `/login?next=<path>` (`lib/safeNext.ts` accepts same-site paths only), and sends signed-in users away from `/login` and `/register`. `/auth/callback` exchanges email-confirmation codes. Email confirmation is off on the project as last seen (it can be changed in the Supabase dashboard). `/forgot-password` is a labelled placeholder. Clients are in `lib/supabase/`; `lib/useSession.ts` gives the session email; `lib/api.ts` has `authHeaders()`.
- **Landing `/`:** hero, docket, chat (`ChatEntry`), compare, "when it is not sure", evidence, "where it stops", footer with licences. `/about` has the raw metrics (English only). The 5-question limit applies to anonymous visitors only; a logged-in user is unlimited on the landing page too.
- **Dashboard** (`/dashboard/*`): Workspace (real chat), Mapping (real), Rulings (real), **Case history (real)**, **Settings (real)**, Documents (preview: nothing stored or read). The Workspace attach control is a preview. The "Preview: sample data" strip stays on Documents and the Workspace; it is hidden on Mapping, Rulings, History and Settings. `SHOW_SAMPLE_SIGNS` stays `true`.
- **Saved history:** a logged-in user's mapped answer saves one row in `public.case_history` (question, offence date, code, section, heading, flagged, language) plus a nullable jsonb `result` holding the finished answer card (`{v:1, card, meta}`: Issue, Rule as statute text, Application, Conclusion parts, `rule_truncated`, offence date and its source, notices, language, sources text) from `ChatEntry` through `lib/caseHistory.ts`. The Application is saved as generated text and is shown with its "Generated text" label, collapsed by default. A result over about 110000 bytes is skipped and the row is saved without it; if the insert is refused with a result, it is retried once without. Failures are ignored quietly; nothing is saved for anonymous visitors. Answers are private to the user (owner-only row-level security) and are removed when the row is deleted, with Clear all, or with the account. The table, its row-level security (read and delete own rows, insert listed columns including `result`, update only `starred`) and `delete_my_account()` live in Supabase, not in this repo (unverified from the repo). History supports search, filters, stars, Open (carries the question through `sessionStorage` key `lawshift-carry` and the row id through `lawshift-open`; the Workspace then fetches that row's `result` and shows a read-only saved card, `components/AnswerCard.tsx` and `components/dashboard/SavedAnswer.tsx`, with "Ask a follow-up" and "Run again"; rows with no result fall back to the question in the composer), delete and Clear all.
- **Settings:** read-only email, default answer language, password change (`updateUser`), account deletion (`delete_my_account` RPC, then sign out and `/?account=deleted`).
- `ChatEntry` props: `hideCounter`, `hideExamples`, `initialDraft`, `unlimited`.
- i18n (EN/HI/MR): `lib/landingCopy.ts`, `lib/dashboardCopy.ts`, `lib/authCopy.ts`, `lib/i18n.ts`. Shared: `components/CodeCompare.tsx`, `lib/wordDiff.ts`, `lib/useRulingsGroup.ts`.
- Unused leftovers: `components/dashboard/ComingNext.tsx`, `lib/useLatestRulings.ts`, old keys `mapWill`, `rulWill`, `soon*`, `stCurrent`, `stDeleteDone` in `dashboardCopy.ts`. `frontend/_archive/` is old work; do not copy from it.

## 7. Data

- `data/clean/mapping.jsonl`: 562 IPC-BNS rows (section 294, partial 122, merged 117, dropped 29). `statutes.jsonl`: 1059 BNS/BNSS/BSA sections (text carries a `[Context:...]` prefix). `ipc_statutes.jsonl`: 562 IPC sections built from the mapping.
- `data/rulings_index.json`: built by `scripts/build_rulings_index.py` from the open court archive (CC BY 4.0, Dattam Labs). Supreme Court: 200 most recent. Bombay High Court: a weekly sample. The archive lags the courts and its dates can be wrong.
- `frontend/src/data/rulings.ts`: curated entries, all `verified:false`. `HIDE_UNVERIFIED` is `false` and must be `true` before launch.
- `models/` is git-ignored (about 1.3 GB). A fresh clone cannot run retrieval without it.

## 8. Regression suite (in the repo)

```
.venv/bin/python scripts/regression/run_all.py        # no Ollama, no live backend
.venv/bin/pytest tests/                                # hardening, HTTP routes, number guard
```

It calls `handle_query` in-process with Stage 4 and 5 stubbed. Expectations are in `scripts/regression/expectations.json` and sit beside the case files; the runner reports FAIL and the delta. Last recorded: **12 PASS, 0 FAIL, 1 INFO** (PROCESS_LOG section 32; not re-run when this file was written). Covers diagnosis 9/9, fact-free 30 (27 `missing_facts` + 3 `missing_date`), false-block 0/285, Stage 1 44/44, paper Recall@5 **0.8412** (535/636) vs production **0.8381** (533/636), `bif85_labeled` **48/85**, code-mismatch 6/6, section_lookup 7/7, date-conflict, rejected-options, quota stub 5,5,5,5,4. The informational first-85 bifurcation count is 52. The 2-question recall gap is the year-as-section parse ("BNSS 2023" read as section 2023).

## 9. Known limits (state plainly)

- The Application can say more than the user did; it can assert facts not given. A "Generated text" line is shown above it. The Rule can be reworded (5 of 60 in one check).
- The checker only sees the Rule and the fixed Conclusion, so it cannot see the Application; its verdict on identical input can differ between runs.
- Translation can change number words and how firm a sentence sounds; the guard checks digits only.
- Stage 1 does not parse ISO dates. Bifurcation fires on 48 of 85 labelled questions. Writer runs are not reproducible (no seed); "0 of 40 fabricated" was a hand review of the older generated Conclusions.
- Date locks and rate limits reset on restart. A session-token problem shows in the chat as "Unexpected response" (from reading the code; not reproduced live).
- Documents page and the Workspace attach control are previews. Forgot-password is a placeholder. Featured rulings are all `verified:false`.
- The 390px layout has about 12 to 14 px of horizontal overflow (Compare cards and evidence rows). The Mapping page's Hindi "no equivalent" bullet starts with "Dropped:" in English.
- LawShift picks the substantive code from the offence date and does not model procedure; High Courts differ on which procedural code applies to older offences. The mapping table is community-maintained.

## 10. Open work, in order

1. Native Hindi and Marathi review of every AI draft, collected in one document. Drafts live in `landingCopy.ts`, `dashboardCopy.ts`, `authCopy.ts` and `i18n.ts` (chat fallbacks, `fixedConclusion`, `generatedNote`, offence-date lines, number-guard note); curated ruling titles are English only.
2. The Application text: the label is done. Option B hides it behind a toggle and shows the verbatim statute as the Rule; option C removes it. Needs the owner's choice.
3. Fix the year-as-section parse (recovers the 2 held-out questions); re-run the suite.
4. Cleanups: move three procedural Bombay outcomes to `BOMBAY_OUTCOMES_EXCLUDED` in `scripts/build_rulings_index.py` (which three: unverified); delete `ComingNext.tsx`, `useLatestRulings.ts` and unused copy keys; exclude `frontend/_archive` from the type check; a README on obtaining `models/`.
5. Document storage and a real Workspace attach control (upload, extract, confirm the date, lock it).
6. Deployment: a rented 24 GB GPU host, or the Mac behind a tunnel. Set `LAWSHIFT_ALLOWED_ORIGINS` and `LAWSHIFT_TRUST_PROXY=1` behind a trusted proxy, set `HIDE_UNVERIFIED` to `true`, and keep auth on before any public URL.
7. Owner checks: read the featured Supreme Court judgments before setting `verified:true`; Mapping and Rulings in HI and MR.

## 11. Files to read first

`CLAUDE.md`, `DESIGN.md`, `PRODUCT.md`, `PROCESS_LOG.md` (sections 22-32 for the live pipeline), `app/main.py` (`handle_query`, `resolve_bifurcation`), `app/schemas.py`, `app/stage3.py`, `src/stage4_generate.py`, `frontend/src/middleware.ts`, `frontend/src/components/ChatEntry.tsx`, `frontend/src/lib/caseHistory.ts`, `frontend/src/lib/dashboardCopy.ts`, `frontend/src/data/rulings.ts`, `scripts/regression/run_all.py`.
