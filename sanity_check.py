import json

import numpy as np
import open_clip
import torch

MODEL_NAME = "ViT-B-32"
PRETRAINED = "openai"

# "boredom" and "mild boredom" are both included here (not just the plain
# per-query loop below), because we also want to directly compare them -
# see the comparison section at the bottom of main().
QUERIES = ["peaceful", "frightening", "joyful", "melancholy", "boredom", "mild boredom"]
TOP_K = 5

# how many top results to compare for overlap between the two queries below
COMPARE_TOP_K = 10
COMPARE_PAIR = ("boredom", "mild boredom")


def main():
    # load what embed_images.py already computed - nothing gets re-embedded here
    embeddings = np.load("data/clip_embeddings.npy")
    uids = json.loads(open("data/clip_uids.json").read())

    # uid -> full metadata record, so we can print titles/makers for matches
    meta = {}
    with open("data/paintings_raw.jsonl") as f:
        for line in f:
            item = json.loads(line)
            meta[item["uid"]] = item

    # load the same CLIP model used for the images - this time we only need
    # its text side, so the image-preprocessing transform (2nd return value)
    # is discarded
    model, _, _ = open_clip.create_model_and_transforms(MODEL_NAME, pretrained=PRETRAINED)
    tokenizer = open_clip.get_tokenizer(MODEL_NAME)
    model.eval()

    with torch.no_grad():  # inference only, no need to track gradients
        tokens = tokenizer(QUERIES)
        text_feats = model.encode_text(tokens)
        # unit-length-normalise, so a dot product = cosine similarity later
        text_feats = text_feats / text_feats.norm(dim=-1, keepdim=True)
    text_feats = text_feats.numpy()

    # one matrix multiply gives every query's similarity to every image at once:
    # (n_queries x 512) @ (512 x n_images) -> (n_queries x n_images)
    sims = text_feats @ embeddings.T

    def top_matches(query_idx, k):
        """Return the uids of the k most-similar paintings to a given query."""
        top_idx = np.argsort(-sims[query_idx])[:k]
        return [uids[i] for i in top_idx]

    for qi, query in enumerate(QUERIES):
        print(f"\n=== '{query}' ===")
        for idx in np.argsort(-sims[qi])[:TOP_K]:
            uid = uids[idx]
            item = meta.get(uid, {})
            score = sims[qi, idx]
            # uid included here too (not just title/maker) so results can be
            # matched back to the downloaded image files in data/images/
            print(f"  {score:.3f}  {uid}  {item.get('title')}  —  {item.get('maker')}")

    # --- does the qualifier "mild" actually change anything? ---
    word_a, word_b = COMPARE_PAIR
    ia, ib = QUERIES.index(word_a), QUERIES.index(word_b)

    # similarity between the two QUERY TEXTS themselves (not via any image) -
    # if this is very close to 1.0, CLIP barely distinguishes the two phrases
    text_to_text_sim = float(text_feats[ia] @ text_feats[ib])

    # do the two queries actually return different paintings in practice?
    top_a = set(top_matches(ia, COMPARE_TOP_K))
    top_b = set(top_matches(ib, COMPARE_TOP_K))
    overlap = top_a & top_b

    print(f"\n=== '{word_a}' vs '{word_b}' ===")
    print(f"  text-to-text cosine similarity: {text_to_text_sim:.3f}")
    print(
        f"  top-{COMPARE_TOP_K} image overlap: {len(overlap)}/{COMPARE_TOP_K} paintings shared"
    )


if __name__ == "__main__":
    main()
