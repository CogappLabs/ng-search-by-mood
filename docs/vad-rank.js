// JS port of vad_rank.py / description_rank.py - both are "rank paintings by
// Euclidean distance between the query's NRC-VAD score and a precomputed
// per-painting VAD table", just pointed at different data files (colour vs
// description). createVadRanker() captures that shared logic once.

import { scoreQuery } from "./vad-lexicon.js";

export function createVadRanker(dataUrl) {
  let paintings = null; // [{uid, valence, arousal, dominance}, ...]

  async function load() {
    if (paintings) return;
    paintings = await fetch(dataUrl).then((r) => r.json());
  }

  // Returns [[uid, distance], ...] best match (smallest distance) first, or
  // [] if nothing in the query was recognised - this mode is entirely
  // lexicon-driven, so "recognised nothing" means there's no real signal to
  // rank by, not a reason to confidently return whatever sits near neutral.
  // `precomputedVad` lets a caller that already called scoreQuery() (e.g.
  // app.js, running all three modes per search) skip a redundant lookup -
  // falls back to calling it here if not given.
  async function rankWithScores(query, precomputedVad) {
    await load();
    const { vad, recognized } = precomputedVad ?? (await scoreQuery(query));
    if (!recognized) return [];
    const [qv, qa, qd] = vad;
    const scored = paintings.map((p) => {
      const dv = p.valence - qv;
      const da = p.arousal - qa;
      const dd = p.dominance - qd;
      return [p.uid, Math.sqrt(dv * dv + da * da + dd * dd)];
    });
    scored.sort((a, b) => a[1] - b[1]);
    return scored;
  }

  async function rankUids(query, precomputedVad) {
    return (await rankWithScores(query, precomputedVad)).map(([uid]) => uid);
  }

  return { rankWithScores, rankUids };
}

// this module's own default instance - colour-derived VAD, matching
// vad_rank.py (colour mode). description-rank.js uses the same factory
// pointed at the description-derived table instead.
export const { rankWithScores, rankUids } = createVadRanker("data/colour_vad.json");
