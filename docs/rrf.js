// JS port of rrf_search.py's fuse() - combines any number of rankers'
// orderings into one fused ranking via Reciprocal Rank Fusion. Only uses
// each ranker's ORDER, not its raw score, since e.g. CLIP similarity and
// VAD distance aren't on comparable scales.

const RRF_K = 60; // same constant as rrf_search.py (Cormack, Clarke & Buettcher 2009)

// `rankers` is {name: asyncRankUidsFn}. Returns {ranked: [uid, ...], scores: {uid: score}}.
export async function fuse(query, rankers) {
  const rankMaps = await Promise.all(
    Object.values(rankers).map(async (rankFn) => {
      const order = await rankFn(query);
      const map = new Map();
      order.forEach((uid, i) => map.set(uid, i + 1)); // ranks start at 1
      return map;
    })
  );

  // only paintings present in EVERY ranker are considered, same as the
  // Python version (a handful of paintings are missing from one ranker or
  // another - e.g. no description, or no downloaded image)
  let candidates = new Set(rankMaps[0].keys());
  for (const map of rankMaps.slice(1)) {
    candidates = new Set([...candidates].filter((uid) => map.has(uid)));
  }

  const scores = {};
  for (const uid of candidates) {
    scores[uid] = rankMaps.reduce((sum, map) => sum + 1 / (RRF_K + map.get(uid)), 0);
  }

  const ranked = [...candidates].sort((a, b) => scores[b] - scores[a]);
  return { ranked, scores };
}
