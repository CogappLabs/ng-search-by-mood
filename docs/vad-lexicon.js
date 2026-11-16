// Scores free text against the NRC-VAD lexicon by calling a tiny Cloudflare
// Worker (see worker/src/index.js) rather than doing the lookup here in the
// browser. The lexicon's licence prohibits redistributing the dataset
// itself ("No Redistribution... you may not otherwise permit third parties
// to use it"), so unlike embeddings.bin/colour_vad.json/etc, it can't be
// shipped as a static file for GitHub Pages to serve - only the Worker's
// own deployment holds it, and it only ever returns a derived (valence,
// arousal, dominance) triple for whatever text was sent, never the lexicon
// itself. Same contract as the old version of this file (and vad_lexicon.py),
// just computed on Cloudflare instead of in this browser.

const WORKER_URL = "https://ng-mood-lexicon.emilyo-660.workers.dev";

// Returns { vad: [valence, arousal, dominance], recognized } - `recognized`
// is false only when literally nothing in the query matched the lexicon
// (see worker/src/index.js), which callers use to tell a genuinely
// unrecognised query ("hdgjgdjhgd") apart from one that just happens to
// land near neutral.
export async function scoreQuery(text) {
  const url = `${WORKER_URL}/?q=${encodeURIComponent(text)}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`lexicon scoring failed: ${res.status} ${res.statusText}`);
  }
  const { valence, arousal, dominance, recognized } = await res.json();
  return { vad: [valence, arousal, dominance], recognized };
}
