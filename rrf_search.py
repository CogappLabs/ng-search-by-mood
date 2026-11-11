import json

from clip_rank import rank_uids as clip_rank_uids
from vad_rank import rank_uids as vad_rank_uids

RRF_K = 60  # standard constant from the Reciprocal Rank Fusion literature
# (Cormack, Clarke & Buettcher 2009) - large enough that a painting ranked
# e.g. 1st vs 5th by one method doesn't swing the fused score wildly

QUERIES = ["peaceful", "frightening", "joyful", "melancholy", "boredom", "mild boredom"]
TOP_K = 5
COMPARE_TOP_K = 10
COMPARE_PAIR = ("boredom", "mild boredom")


def fuse(query):
    """Combine CLIP's ranking and VAD's ranking for one query into a single
    fused ranking using Reciprocal Rank Fusion: each painting's fused score
    is 1/(RRF_K + its CLIP rank) + 1/(RRF_K + its VAD rank), with ranks
    starting at 1. This only uses each method's ORDERING, not its raw
    scores, which sidesteps the fact that CLIP cosine similarity and VAD
    distance aren't on comparable scales. Only paintings that appear in
    both rankings are considered (a handful of paintings have colour data
    but no downloaded image, or vice versa).

    Returns (uids_best_first, {uid: fused_score})."""
    clip_order = clip_rank_uids(query)
    vad_order = vad_rank_uids(query)
    clip_rank_of = {uid: i + 1 for i, uid in enumerate(clip_order)}
    vad_rank_of = {uid: i + 1 for i, uid in enumerate(vad_order)}
    candidates = clip_rank_of.keys() & vad_rank_of.keys()

    scores = {
        uid: 1 / (RRF_K + clip_rank_of[uid]) + 1 / (RRF_K + vad_rank_of[uid])
        for uid in candidates
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
        print(f"\n=== '{query}' (fused: CLIP + VAD via RRF) ===")
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
