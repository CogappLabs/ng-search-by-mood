import json

import clip_rank
import vad_rank
import description_rank

RRF_K = 60  # standard constant from the Reciprocal Rank Fusion literature
# (Cormack, Clarke & Buettcher 2009) - large enough that a painting ranked
# e.g. 1st vs 5th by one method doesn't swing the fused score wildly

# every ranker fused by default - each is just "give me an ordered list of
# uids for this query", so adding a new signal later just means adding
# another entry here, nothing else in fuse() needs to change
RANKERS = {
    "clip": clip_rank.rank_uids,
    "colour": vad_rank.rank_uids,
    "description": description_rank.rank_uids,
}

QUERIES = ["peaceful", "frightening", "joyful", "melancholy", "boredom", "mild boredom"]
TOP_K = 5
COMPARE_TOP_K = 10
COMPARE_PAIR = ("boredom", "mild boredom")


def fuse(query, rankers=None):
    """Combine any number of rankers' orderings for one query into a single
    fused ranking using Reciprocal Rank Fusion: each painting's fused score
    is the sum of 1/(RRF_K + its rank) across every ranker it appears in,
    with ranks starting at 1. This only uses each ranker's ORDERING, not its
    raw scores, which sidesteps the fact that e.g. CLIP cosine similarity
    and VAD distance aren't on comparable scales - a ranker can be added
    (like `description`, scoring the curator's own written text) without
    needing to figure out how its numbers relate to anyone else's.

    `rankers` defaults to every entry in RANKERS (currently CLIP, colour-VAD
    and description-VAD); pass a subset dict to fuse only some of them.

    Only paintings that appear in EVERY included ranker are considered (a
    handful of paintings are missing from one or another - e.g. no
    downloaded image, or no curatorial description at all).

    Returns (uids_best_first, {uid: fused_score})."""
    rankers = rankers or RANKERS
    rank_maps = []
    for rank_fn in rankers.values():
        order = rank_fn(query)
        rank_maps.append({uid: i + 1 for i, uid in enumerate(order)})

    candidates = set.intersection(*(set(m) for m in rank_maps))
    scores = {
        uid: sum(1 / (RRF_K + m[uid]) for m in rank_maps) for uid in candidates
    }
    ranked = sorted(candidates, key=lambda uid: -scores[uid])
    return ranked, scores


def main():
    meta = {}
    with open("data/paintings_raw.jsonl") as f:
        for line in f:
            item = json.loads(line)
            meta[item["uid"]] = item

    fused_top = {}
    for query in QUERIES:
        order, scores = fuse(query)
        fused_top[query] = order[:COMPARE_TOP_K]
        print(f"\n=== '{query}' (fused: {', '.join(RANKERS)} via RRF) ===")
        for uid in order[:TOP_K]:
            item = meta.get(uid, {})
            print(f"  {scores[uid]:.4f}  {uid}  {item.get('title')}  —  {item.get('maker')}")

    # same qualifier check as the standalone CLIP and VAD scripts, so all
    # three can be compared side by side
    word_a, word_b = COMPARE_PAIR
    top_a, top_b = set(fused_top[word_a]), set(fused_top[word_b])
    overlap = top_a & top_b
    print(f"\n=== '{word_a}' vs '{word_b}' (fused) ===")
    print(f"  top-{COMPARE_TOP_K} fused overlap: {len(overlap)}/{COMPARE_TOP_K} paintings shared")


if __name__ == "__main__":
    main()
