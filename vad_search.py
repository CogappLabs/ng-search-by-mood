import numpy as np
import pandas as pd

from vad_lexicon import load_lexicon, score_query

# same test words as sanity_check.py (the CLIP version), so the two
# approaches can be compared directly on identical queries
QUERIES = ["peaceful", "frightening", "joyful", "melancholy", "boredom", "mild boredom"]
TOP_K = 5
COMPARE_TOP_K = 10
COMPARE_PAIR = ("boredom", "mild boredom")


def main():
    paintings = pd.read_parquet("data/colour_vad.parquet")
    # one (n_paintings x 3) matrix of every painting's (valence, arousal, dominance)
    painting_vad = paintings[["valence", "arousal", "dominance"]].to_numpy()

    lexicon = load_lexicon()

    # score every query up front so we can reuse them below for the
    # boredom/mild-boredom comparison without recomputing anything
    query_vads = {q: np.array(score_query(q, lexicon)) for q in QUERIES}

    def top_matches(query_vec, k):
        """Rank every painting by Euclidean distance from query_vec in
        valence/arousal/dominance space - closest first - and return the
        top k as (distance, row) pairs."""
        dists = np.linalg.norm(painting_vad - query_vec, axis=1)
        top_idx = np.argsort(dists)[:k]
        return [(dists[i], paintings.iloc[i]) for i in top_idx]

    for query in QUERIES:
        vad = query_vads[query]
        print(f"\n=== '{query}'  (v={vad[0]:.3f}, a={vad[1]:.3f}, d={vad[2]:.3f}) ===")
        for dist, row in top_matches(vad, TOP_K):
            print(f"  {dist:.3f}  {row.uid}  {row.title}  —  {row.maker}")

    # --- does the qualifier "mild" actually change anything here? ---
    word_a, word_b = COMPARE_PAIR
    vad_a, vad_b = query_vads[word_a], query_vads[word_b]

    # distance between the two QUERY VAD POINTS themselves (not via any
    # painting) - if this is near 0, the lexicon treats the two phrases as
    # nearly identical, same idea as the text-to-text check in the CLIP version
    query_to_query_dist = float(np.linalg.norm(vad_a - vad_b))

    top_a = {row.uid for _, row in top_matches(vad_a, COMPARE_TOP_K)}
    top_b = {row.uid for _, row in top_matches(vad_b, COMPARE_TOP_K)}
    overlap = top_a & top_b

    print(f"\n=== '{word_a}' vs '{word_b}' ===")
    print(f"  '{word_a}' VAD:       {tuple(round(float(x), 3) for x in vad_a)}")
    print(f"  '{word_b}' VAD: {tuple(round(float(x), 3) for x in vad_b)}")
    print(f"  distance between the two query points: {query_to_query_dist:.3f}")
    print(
        f"  top-{COMPARE_TOP_K} painting overlap: {len(overlap)}/{COMPARE_TOP_K} paintings shared"
    )


if __name__ == "__main__":
    main()
