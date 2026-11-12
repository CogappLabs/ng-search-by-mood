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

  // Returns [[uid, distance], ...] best match (smallest distance) first.
  // Lower is better here - it's a distance, not a similarity.
  async function rankWithScores(query) {
    await load();
    const [qv, qa, qd] = await scoreQuery(query);
    const scored = paintings.map((p) => {
      const dv = p.valence - qv;
      const da = p.arousal - qa;
      const dd = p.dominance - qd;
      return [p.uid, Math.sqrt(dv * dv + da * da + dd * dd)];
    });
    scored.sort((a, b) => a[1] - b[1]);
    return scored;
  }

  async function rankUids(query) {
    return (await rankWithScores(query)).map(([uid]) => uid);
  }

  return { rankWithScores, rankUids };
}

// this module's own default instance - colour-derived VAD, matching
// vad_rank.py (colour mode). description-rank.js uses the same factory
// pointed at the description-derived table instead.
export const { rankWithScores, rankUids } = createVadRanker("data/colour_vad.json");
