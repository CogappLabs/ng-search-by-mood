import json

import numpy as np
import open_clip
import torch

MODEL_NAME = "ViT-B-32"
PRETRAINED = "openai"

# module-level cache: the model and embeddings only get loaded once per
# process, no matter how many times rank_uids() is called
_model = None
_tokenizer = None
_embeddings = None
_uids = None


def _load():
    global _model, _tokenizer, _embeddings, _uids
    if _model is not None:
        return
    _embeddings = np.load("data/clip_embeddings.npy")
    _uids = json.loads(open("data/clip_uids.json").read())
    _model, _, _ = open_clip.create_model_and_transforms(MODEL_NAME, pretrained=PRETRAINED)
    _tokenizer = open_clip.get_tokenizer(MODEL_NAME)
    _model.eval()


def rank_with_scores(query):
    """Return every embedded painting as (uid, cosine_similarity), best-match
    (highest similarity) first, comparing the query's CLIP text embedding
    against each painting's precomputed CLIP image embedding (see
    embed_images.py)."""
    _load()
    with torch.no_grad():
        tokens = _tokenizer([query])
        text_feat = _model.encode_text(tokens)
        text_feat = text_feat / text_feat.norm(dim=-1, keepdim=True)
    text_feat = text_feat.numpy()[0]
    sims = _embeddings @ text_feat
    order = np.argsort(-sims)
    return [(_uids[i], float(sims[i])) for i in order]


def rank_uids(query):
    """Same as rank_with_scores(), but just the ordered uids - used where
    only the ranking matters, not the raw similarity value (e.g. fusion)."""
    return [uid for uid, _ in rank_with_scores(query)]
