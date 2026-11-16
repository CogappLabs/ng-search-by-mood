// JS port of rrf_search.py's fuse() - combines any number of rankers'
// orderings into one fused ranking via Reciprocal Rank Fusion. Only uses
// each ranker's ORDER, not its raw score, since e.g. CLIP similarity and
// VAD distance aren't on comparable scales.

const RRF_K = 60; // same constant as rrf_search.py (Cormack, Clarke & Buettcher 2009)

// Core RRF maths over orderings a caller has ALREADY computed - `orders` is
// {name: [uid, ...]}. Split out from fuse() so app.js can reuse the clip/
// colour/description orderings it already ran for their own modes, instead
// of running each ranker a second time just for the combined mode.
// Returns {ranked: [uid, ...], scores: {uid: score}}.
export function fuseOrders(orders) {
  const rankMaps = Object.values(orders).map((order) => {
    const map = new Map();
    order.forEach((uid, i) => map.set(uid, i + 1)); // ranks start at 1
    return map;
  });

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

// `rankers` is {name: asyncRankUidsFn} - runs each ranker itself, then fuses
// via fuseOrders(). Kept for parity with rrf_search.py's fuse(); app.js uses
// fuseOrders() directly instead, since it already has these orderings.
export async function fuse(query, rankers) {
  const entries = Object.entries(rankers);
  const orders = await Promise.all(entries.map(([, rankFn]) => rankFn(query)));
  const ordersByName = {};
  entries.forEach(([name], i) => {
    ordersByName[name] = orders[i];
  });
  return fuseOrders(ordersByName);
}
