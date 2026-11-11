import json

import numpy as np
import open_clip
import torch

from vad_lexicon import load_lexicon, score_query

MODEL_NAME = "ViT-B-32"
PRETRAINED = "openai"

# Small, fixed word sets used only as a generic "opposite mood" reference
# point - not shown to users, not part of the open-vocabulary search itself.
# See rank_with_scores() for how they're used.
POSITIVE_ANCHORS = ["joyful", "happy", "cheerful", "pleasant", "delightful"]
NEGATIVE_ANCHORS = ["sorrowful", "sad", "grim", "unpleasant", "bleak"]

# module-level cache: the model, embeddings, lexicon and anchor vectors only
# get loaded/computed once per process, no matter how many times
# rank_uids()/rank_with_scores() is called
_model = None
_tokenizer = None
_embeddings = None
_uids = None
_lexicon = None
_positive_anchor_vec = None
_negative_anchor_vec = None


def _embed_texts(texts):
    """Run a list of strings through CLIP's text encoder, returning one
    unit-length vector per string."""
    with torch.no_grad():
        tokens = _tokenizer(texts)
        feats = _model.encode_text(tokens)
        feats = feats / feats.norm(dim=-1, keepdim=True)
    return feats.numpy()


def _average_embedding(words):
    """Embed several words and collapse them to a single unit-length vector
    (their mean, re-normalised) - used to build a less idiosyncratic
    "generic positive/negative mood" reference point than any one word."""
    vecs = _embed_texts(words)
    avg = vecs.mean(axis=0)
    return avg / np.linalg.norm(avg)


def _load():
    global _model, _tokenizer, _embeddings, _uids
    global _lexicon, _positive_anchor_vec, _negative_anchor_vec
    if _model is not None:
        return
    _embeddings = np.load("data/clip_embeddings.npy")
    _uids = json.loads(open("data/clip_uids.json").read())
    _model, _, _ = open_clip.create_model_and_transforms(MODEL_NAME, pretrained=PRETRAINED)
    _tokenizer = open_clip.get_tokenizer(MODEL_NAME)
    _model.eval()
    _lexicon = load_lexicon()
    _positive_anchor_vec = _average_embedding(POSITIVE_ANCHORS)
    _negative_anchor_vec = _average_embedding(NEGATIVE_ANCHORS)


def rank_with_scores(query):
    """Return every embedded painting as (uid, margin), best-match first.

    Rather than ranking purely by how similar a painting is to `query` in
    absolute terms, this computes a CONTRASTIVE margin: similarity to the
    query minus similarity to a small, fixed set of generically opposite-
    mood words. This catches paintings that read as MORE aligned with the
    opposite mood than with the query, even when their raw similarity to
    the query is still fairly high in isolation - e.g. a devotional "Man of
    Sorrows" painting scored 0.233 on "joyful" taken alone (high enough to
    reach the top results), but scored higher still, 0.252, on "sorrowful" -
    a plain similarity ranking never saw that second number at all.

    Which contrast set to use (sorrowful-ish vs joyful-ish words) is picked
    automatically per query, from the query's own valence sign via the
    NRC-VAD lexicon (a positive-valence query gets contrasted against the
    negative anchor words, and vice versa) - so this still works for
    arbitrary open-ended text, not just a fixed list of known mood words.
    """
    _load()
    query_vec = _embed_texts([query])[0]

    valence, _, _ = score_query(query, _lexicon)
    contrast_vec = _negative_anchor_vec if valence >= 0 else _positive_anchor_vec

    query_sims = _embeddings @ query_vec
    contrast_sims = _embeddings @ contrast_vec
    margins = query_sims - contrast_sims

    order = np.argsort(-margins)
    return [(_uids[i], float(margins[i])) for i in order]


def rank_uids(query):
    """Same as rank_with_scores(), but just the ordered uids - used where
    only the ranking matters, not the raw margin value (e.g. fusion)."""
    return [uid for uid, _ in rank_with_scores(query)]
