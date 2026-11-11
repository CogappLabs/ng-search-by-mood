import numpy as np
import pandas as pd

from vad_lexicon import load_lexicon, score_query

# module-level cache, same idea as vad_rank.py/clip_rank.py
_paintings = None
_lexicon = None


def _load():
    global _paintings, _lexicon
    if _paintings is not None:
        return
    _paintings = pd.read_parquet("data/description_vad.parquet")
    _lexicon = load_lexicon()


def rank_with_scores(query):
    """Return every painting as (uid, distance), best-match (smallest
    distance) first, comparing the query's NRC-VAD score against each
    painting's DESCRIPTION-derived valence/arousal/dominance score (see
    description_vad.py) - the curator's own written words about the
    painting, not its image or colours. Lower is better - it's a distance,
    not a similarity.

    ~34 paintings with no curatorial description at all are absent from
    this ranking entirely (see description_vad.py)."""
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
