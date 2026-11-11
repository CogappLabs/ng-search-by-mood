import numpy as np
import pandas as pd

from vad_lexicon import load_lexicon, score_query

# module-level cache, same idea as clip_rank.py
_paintings = None
_lexicon = None


def _load():
    global _paintings, _lexicon
    if _paintings is not None:
        return
    _paintings = pd.read_parquet("data/colour_vad.parquet")
    _lexicon = load_lexicon()


def rank_with_scores(query):
    """Return every painting as (uid, distance), best-match (smallest
    distance) first, comparing the query's NRC-VAD score against each
    painting's colour-derived valence/arousal/dominance score (see
    colour_vad.py). Note: unlike CLIP's cosine similarity, LOWER is better
    here - it's a distance, not a similarity."""
    _load()
    vad = np.array(score_query(query, _lexicon))
    painting_vad = _paintings[["valence", "arousal", "dominance"]].to_numpy()
    dists = np.linalg.norm(painting_vad - vad, axis=1)
    order = np.argsort(dists)
    uids = _paintings.iloc[order]["uid"].tolist()
    return list(zip(uids, (float(d) for d in dists[order])))


def rank_uids(query):
    """Same as rank_with_scores(), but just the ordered uids - used where
    only the ranking matters, not the raw distance value (e.g. fusion)."""
    return [uid for uid, _ in rank_with_scores(query)]
