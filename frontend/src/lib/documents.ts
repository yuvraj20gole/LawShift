import { API_BASE, authHeaders } from "@/lib/api";
import { createClient } from "@/lib/supabase/client";
import type { DocCopy } from "@/lib/documentsCopy";

/** The user's own description of what happened: the search query. Long documents dilute search, so this is short. */
export const FACTS_MIN_CHARS = 20;
export const FACTS_MAX_CHARS = 800;
export const MAX_FILE_BYTES = 10 * 1024 * 1024;

export const BUCKET = "case-documents";

export type DocKind = "pdf" | "image" | "docx";
export type ReadMethod = "typed" | "ocr" | "docx";
export type DateSource = "document" | "edited";

export type DateCandidate = { iso: string; label: string; context: string };

export type Extraction = {
  filename: string;
  kind: DocKind;
  read_method: ReadMethod;
  pages: number;
  char_count: number;
  text: string;
  truncated: boolean;
  date: { iso: string; label: string } | null;
  date_candidates: DateCandidate[];
  warnings: string[];
};

export type StoredDoc = {
  id: string;
  created_at: string;
  filename: string;
  kind: DocKind;
  size_bytes: number;
  read_method: ReadMethod;
  offence_date: string;
  date_source: DateSource;
  /** The user's description (the column is still called extracted_text). */
  extracted_text: string;
  storage_path: string;
};

export type DocErrorKind =
  | "401" | "413" | "415" | "422" | "429" | "503"
  | "network" | "generic" | "save" | "delete" | "download" | "attach" | "detach" | "load";

/** A failure with a kind only: never the server's text, a file name or a token. */
export class DocError extends Error {
  kind: DocErrorKind;
  constructor(kind: DocErrorKind) {
    super(kind);
    this.kind = kind;
  }
}

/** The localised, user-facing sentence for a failure. Unknown errors become the generic one. */
export function docErrorMessage(err: unknown, C: DocCopy): string {
  const kind = err instanceof DocError ? err.kind : "generic";
  switch (kind) {
    case "401": return C.err401;
    case "413": return C.err413;
    case "415": return C.err415;
    case "422": return C.err422;
    case "429": return C.err429;
    case "503": return C.err503;
    case "network": return C.errNetwork;
    case "save": return C.errSave;
    case "delete": return C.errDelete;
    case "download": return C.errDownload;
    case "attach": return C.errAttach;
    case "detach": return C.errDetach;
    case "load": return C.loadError;
    default: return C.errGeneric;
  }
}

const ISO = /^\d{4}-\d{2}-\d{2}$/;
const KINDS: DocKind[] = ["pdf", "image", "docx"];
const METHODS: ReadMethod[] = ["typed", "ocr", "docx"];

function statusKind(status: number): DocErrorKind {
  return status === 401 || status === 413 || status === 415 || status === 422 || status === 429 || status === 503
    ? (String(status) as DocErrorKind)
    : "generic";
}

/** Checks the type and size before anything is sent. */
export function checkFile(file: File): DocErrorKind | null {
  if (!/\.(pdf|jpe?g|png|docx)$/i.test(file.name)) return "415";
  if (file.size > MAX_FILE_BYTES) return "413";
  return null;
}

function parseExtraction(raw: unknown): Extraction {
  if (!raw || typeof raw !== "object") throw new DocError("generic");
  const o = raw as Record<string, unknown>;
  if (!KINDS.includes(o.kind as DocKind) || !METHODS.includes(o.read_method as ReadMethod)) {
    throw new DocError("generic");
  }
  const date =
    o.date && typeof o.date === "object" && ISO.test(String((o.date as { iso?: unknown }).iso))
      ? {
          iso: String((o.date as { iso: string }).iso),
          label: String((o.date as { label?: unknown }).label ?? ""),
        }
      : null;
  const candidates = Array.isArray(o.date_candidates)
    ? o.date_candidates
        .filter((c): c is Record<string, unknown> => !!c && typeof c === "object")
        .filter((c) => ISO.test(String(c.iso)))
        .map((c) => ({
          iso: String(c.iso),
          label: String(c.label ?? ""),
          context: String(c.context ?? ""),
        }))
    : [];
  return {
    filename: String(o.filename ?? ""),
    kind: o.kind as DocKind,
    read_method: o.read_method as ReadMethod,
    pages: Number(o.pages) || 0,
    char_count: Number(o.char_count) || 0,
    text: typeof o.text === "string" ? o.text : "",
    truncated: Boolean(o.truncated),
    date,
    date_candidates: candidates,
    warnings: Array.isArray(o.warnings) ? o.warnings.filter((w): w is string => typeof w === "string") : [],
  };
}

/** Sends the file to the backend for reading. The backend stores nothing. */
export async function extractDocument(file: File): Promise<Extraction> {
  const bad = checkFile(file);
  if (bad) throw new DocError(bad);
  let res: Response;
  try {
    const body = new FormData();
    body.append("file", file);
    res = await fetch(`${API_BASE}/api/documents/extract`, {
      method: "POST",
      headers: { ...(await authHeaders()) },
      body,
    });
  } catch {
    throw new DocError("network");
  }
  if (!res.ok) throw new DocError(statusKind(res.status));
  try {
    return parseExtraction(await res.json());
  } catch {
    throw new DocError("generic");
  }
}

function extensionFor(file: File, kind: DocKind): string {
  if (kind === "pdf") return "pdf";
  if (kind === "docx") return "docx";
  return file.type === "image/png" || /\.png$/i.test(file.name) ? "png" : "jpg";
}

const CONTENT_TYPES: Record<string, string> = {
  pdf: "application/pdf",
  jpg: "image/jpeg",
  png: "image/png",
  docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
};

async function currentUserId(): Promise<string> {
  const { data } = await createClient().auth.getSession();
  const id = data.session?.user.id;
  if (!id) throw new DocError("401");
  return id;
}

/**
 * Uploads the file to "<user id>/<uuid>.<ext>", then inserts the row. If the
 * insert fails the uploaded file is removed again, so nothing is left behind.
 */
export async function saveDocument(
  file: File,
  extraction: Extraction,
  description: string,
  offenceDate: string,
  dateSource: DateSource,
): Promise<StoredDoc> {
  if (!ISO.test(offenceDate)) throw new DocError("save");
  const supabase = createClient();
  const uid = await currentUserId();
  const ext = extensionFor(file, extraction.kind);
  const path = `${uid}/${crypto.randomUUID()}.${ext}`;
  try {
    const up = await supabase.storage.from(BUCKET).upload(path, file, {
      contentType: CONTENT_TYPES[ext],
      upsert: false,
    });
    if (up.error) throw new DocError("save");
    const ins = await supabase
      .from("case_documents")
      .insert({
        filename: (file.name || extraction.filename).slice(0, 255),
        kind: extraction.kind,
        size_bytes: file.size,
        read_method: extraction.read_method,
        offence_date: offenceDate,
        date_source: dateSource,
        extracted_text: description.slice(0, FACTS_MAX_CHARS),
        storage_path: path,
      })
      .select()
      .single();
    if (ins.error || !ins.data) {
      await supabase.storage.from(BUCKET).remove([path]).catch(() => undefined);
      throw new DocError("save");
    }
    return ins.data as StoredDoc;
  } catch (e) {
    if (e instanceof DocError) throw e;
    await supabase.storage.from(BUCKET).remove([path]).catch(() => undefined);
    throw new DocError("save");
  }
}

/** The signed-in user's documents, newest first. */
export async function listDocuments(): Promise<StoredDoc[]> {
  try {
    const { data, error } = await createClient()
      .from("case_documents")
      .select("*")
      .order("created_at", { ascending: false });
    if (error || !data) throw new DocError("load");
    return data as StoredDoc[];
  } catch (e) {
    throw e instanceof DocError ? e : new DocError("load");
  }
}

/** Deletes the file first, then the row; if the file cannot be removed the row stays. */
export async function deleteDocument(doc: Pick<StoredDoc, "id" | "storage_path">): Promise<void> {
  try {
    const supabase = createClient();
    const rm = await supabase.storage.from(BUCKET).remove([doc.storage_path]);
    if (rm.error) throw new DocError("delete");
    const del = await supabase.from("case_documents").delete().eq("id", doc.id);
    if (del.error) throw new DocError("delete");
  } catch (e) {
    throw e instanceof DocError ? e : new DocError("delete");
  }
}

export async function deleteAllDocuments(docs: Pick<StoredDoc, "id" | "storage_path">[]): Promise<void> {
  try {
    const supabase = createClient();
    for (let i = 0; i < docs.length; i += 50) {
      const chunk = docs.slice(i, i + 50);
      const rm = await supabase.storage.from(BUCKET).remove(chunk.map((d) => d.storage_path));
      if (rm.error) throw new DocError("delete");
      const del = await supabase.from("case_documents").delete().in("id", chunk.map((d) => d.id));
      if (del.error) throw new DocError("delete");
    }
  } catch (e) {
    throw e instanceof DocError ? e : new DocError("delete");
  }
}

/** A download link that works for 60 seconds. */
export async function signedUrl(storagePath: string, downloadName?: string): Promise<string> {
  try {
    const { data, error } = await createClient()
      .storage.from(BUCKET)
      .createSignedUrl(storagePath, 60, downloadName ? { download: downloadName } : undefined);
    if (error || !data?.signedUrl) throw new DocError("download");
    return data.signedUrl;
  } catch (e) {
    throw e instanceof DocError ? e : new DocError("download");
  }
}

/**
 * Account deletion step: removes every object under "<user id>/" (list, remove, repeat until
 * empty). Throws if listing or removal fails, or if a pass removes nothing, so the caller keeps the account.
 */
export async function purgeUserFiles(): Promise<void> {
  try {
    const supabase = createClient();
    const uid = await currentUserId();
    for (let pass = 0; pass < 200; pass++) {
      const list = await supabase.storage.from(BUCKET).list(uid, { limit: 100 });
      if (list.error) throw new DocError("delete");
      const names = (list.data ?? []).map((f) => f.name).filter(Boolean);
      if (names.length === 0) return;
      const rm = await supabase.storage.from(BUCKET).remove(names.map((n) => `${uid}/${n}`));
      if (rm.error) throw new DocError("delete");
      if (!rm.data || rm.data.length === 0) throw new DocError("delete");
    }
    throw new DocError("delete");
  } catch (e) {
    throw e instanceof DocError ? e : new DocError("delete");
  }
}

async function postJson(path: string, body: unknown, failure: DocErrorKind): Promise<unknown> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(await authHeaders()) },
      body: JSON.stringify(body),
    });
  } catch {
    throw new DocError("network");
  }
  if (res.status === 401) throw new DocError("401");
  if (res.status === 429) throw new DocError("429");
  if (!res.ok) throw new DocError(failure);
  try {
    return await res.json();
  } catch {
    return {};
  }
}

/** Gives the conversation the confirmed offence date and the user's own description (never the document text). */
export async function attachCase(args: {
  conversation_id: string;
  facts_text: string;
  offence_date: string;
  date_source: DateSource;
  filename?: string;
}): Promise<{ offence_date_label: string; code: string }> {
  if (!ISO.test(args.offence_date) || args.facts_text.trim().length < FACTS_MIN_CHARS || args.facts_text.length > FACTS_MAX_CHARS) {
    throw new DocError("attach");
  }
  const body: Record<string, unknown> = { ...args };
  if (!args.filename) delete body.filename;
  else body.filename = args.filename.slice(0, 255);
  const data = (await postJson("/api/case/attach", body, "attach")) as Record<string, unknown>;
  if (data.ok !== true) throw new DocError("attach");
  return { offence_date_label: String(data.offence_date_label ?? ""), code: String(data.code ?? "") };
}

export async function detachCase(conversationId: string): Promise<void> {
  await postJson("/api/case/detach", { conversation_id: conversationId }, "detach");
}

/** "2.4 MB", "310 KB". */
export function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/** The conversation that currently has a document attached (at most one). Module state, not logged. */
let attachedConversation: string | null = null;

export function markAttached(conversationId: string | null): void {
  attachedConversation = conversationId;
}

/**
 * Best-effort detach for leaving the Workspace or logging out. keepalive lets the request finish
 * as the page goes; failures are ignored. Does nothing when no document is attached, so a
 * development double-mount (which attaches nothing) sends nothing, and it cannot fire twice.
 */
export async function detachActiveBestEffort(): Promise<void> {
  const id = attachedConversation;
  if (!id) return;
  attachedConversation = null;
  {
    try {
      await fetch(`${API_BASE}/api/case/detach`, {
        method: "POST",
        keepalive: true,
        headers: { "Content-Type": "application/json", ...(await authHeaders()) },
        body: JSON.stringify({ conversation_id: id }),
      });
    } catch {
      /* best effort */
    }
  }
}
