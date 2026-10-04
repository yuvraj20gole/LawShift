export type Seg = { t: string; hl?: boolean };

/** Compare words without their surrounding punctuation or case. */
const key = (w: string) => w.toLowerCase().replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, "");

function group(words: string[], flags: boolean[]): Seg[] {
  const out: Seg[] = [];
  words.forEach((w, i) => {
    const hl = flags[i];
    const last = out[out.length - 1];
    if (last && !!last.hl === hl) last.t += " " + w;
    else out.push({ t: i === 0 ? w : w, hl: hl || undefined });
  });
  // keep a single space between segments when rendered back to back
  return out.map((s, i) => (i === 0 ? s : { ...s, t: " " + s.t }));
}

/**
 * Word-level diff between two texts (longest common subsequence). Returns the
 * segments of each side with only the words that are NOT in the common
 * sequence marked as highlighted.
 */
export function diffWords(a: string, b: string): { a: Seg[]; b: Seg[] } {
  const wa = a.split(/\s+/).filter(Boolean);
  const wb = b.split(/\s+/).filter(Boolean);
  const ka = wa.map(key);
  const kb = wb.map(key);
  const n = ka.length;
  const m = kb.length;

  // LCS table (Uint16 is enough for sections up to 65k words)
  const w = m + 1;
  const dp = new Uint16Array((n + 1) * w);
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      dp[i * w + j] =
        ka[i] === kb[j] ? dp[(i + 1) * w + j + 1] + 1 : Math.max(dp[(i + 1) * w + j], dp[i * w + j + 1]);
    }
  }
  const fa = new Array<boolean>(n).fill(true);
  const fb = new Array<boolean>(m).fill(true);
  let i = 0;
  let j = 0;
  while (i < n && j < m) {
    if (ka[i] === kb[j]) {
      fa[i] = false;
      fb[j] = false;
      i++;
      j++;
    } else if (dp[(i + 1) * w + j] >= dp[i * w + j + 1]) i++;
    else j++;
  }
  return { a: group(wa, fa), b: group(wb, fb) };
}

/** No counterpart to compare against: show the text with nothing highlighted. */
export function plain(text: string): Seg[] {
  return [{ t: text }];
}
