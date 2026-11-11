import json

import numpy as np
import open_clip
import torch

from vad_lexicon import load_lexicon, score_query

MODEL_NAME = "ViT-B-32"
PRETRAINED = "openai"

# Small, fixed word sets used only as a generic "opposite mood" reference
# point - not shown to users, not part of the open-vocabulary search itself.
# One pair per NRC-VAD axis, since different queries are distinguished by
# different axes: "joy" is mainly a valence word, but "boredom" is mainly a
# (low) AROUSAL word - contrasting it against positive-valence words like
# "happy" rewards anything merely un-happy, including dramatic/violent
# scenes that are plenty exciting, just not joyful. See rank_with_scores().
ANCHORS = {
    "valence": {
        "pos": ["joyful", "happy", "cheerful", "pleasant", "delightful"],
        "neg": ["sorrowful", "sad", "grim", "unpleasant", "bleak"],
    },
    "arousal": {
        "pos": ["exciting", "thrilling", "intense", "electrifying", "stimulating"],
        "neg": ["calm", "sleepy", "tranquil", "sedate", "drowsy"],
    },
    "dominance": {
        "pos": ["powerful", "commanding", "dominant", "assertive", "forceful"],
        "neg": ["submissive", "weak", "helpless", "powerless", "timid"],
    },
}

# module-level cache: the model, embeddings, lexicon and anchor vectors only
# get loaded/computed once per process, no matter how many times
# rank_uids()/rank_with_scores() is called
_model = None
_tokenizer = None
_embeddings = None
_uids = None
_lexicon = None
_anchor_vecs = None  # {"valence": {"pos": vec, "neg": vec}, "arousal": {...}, ...}


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
    "generic anchor" reference point than any one word."""
    vecs = _embed_texts(words)
    avg = vecs.mean(axis=0)
    return avg / np.linalg.norm(avg)


def _load():
    global _model, _tokenizer, _embeddings, _uids, _lexicon, _anchor_vecs
    if _model is not None:
        return
    _embeddings = np.load("data/clip_embeddings.npy")
    _uids = json.loads(open("data/clip_uids.json").read())
    _model, _, _ = open_clip.create_model_and_transforms(MODEL_NAME, pretrained=PRETRAINED)
    _tokenizer = open_clip.get_tokenizer(MODEL_NAME)
    _model.eval()
    _lexicon = load_lexicon()
    _anchor_vecs = {
        axis: {pole: _average_embedding(words) for pole, words in poles.items()}
        for axis, poles in ANCHORS.items()
    }


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

    Which axis to contrast on (valence/arousal/dominance) and which pole
    (e.g. sorrowful-ish vs joyful-ish) is picked automatically per query:
    the query's own (valence, arousal, dominance) is looked up via the
    NRC-VAD lexicon, the axis with the LARGEST magnitude is treated as the
    one that actually defines this query, and the contrast anchor is the
    opposite pole of THAT axis specifically. "joy" is mostly a valence word,
    so it's contrasted against negative-valence anchors; "boredom" is
    mostly a (low) arousal word, so it's contrasted against high-arousal
    anchors instead of positive-valence ones - which stops dramatic/violent
    (high-arousal) paintings from scoring well just for being un-happy.
    """
    _load()
    query_vec = _embed_texts([query])[0]

    vad = score_query(query, _lexicon)
    axes = ("valence", "arousal", "dominance")
    dominant_axis = max(range(3), key=lambda i: abs(vad[i]))
    axis_name = axes[dominant_axis]
    pole = "pos" if vad[dominant_axis] >= 0 else "neg"
    contrast_pole = "neg" if pole == "pos" else "pos"
    contrast_vec = _anchor_vecs[axis_name][contrast_pole]

    query_sims = _embeddings @ query_vec
    contrast_sims = _embeddings @ contrast_vec
    margins = query_sims - contrast_sims

    order = np.argsort(-margins)
    return [(_uids[i], float(margins[i])) for i in order]


def rank_uids(query):
    """Same as rank_with_scores(), but just the ordered uids - used where
    only the ranking matters, not the raw margin value (e.g. fusion)."""
    return [uid for uid, _ in rank_with_scores(query)]
