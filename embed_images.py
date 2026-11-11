import json
import pathlib

import numpy as np
import open_clip
import torch
from PIL import Image
from tqdm import tqdm

IMAGES_DIR = pathlib.Path("data/images")
OUT_EMB = pathlib.Path("data/clip_embeddings.npy")
OUT_UIDS = pathlib.Path("data/clip_uids.json")
MODEL_NAME = "ViT-B-32"
PRETRAINED = "openai"  # OpenAI's original CLIP weights, loaded via open_clip
BATCH_SIZE = 32


def main():
    # use a GPU if one's available, otherwise fall back to CPU (fine at this scale)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"loading {MODEL_NAME}/{PRETRAINED} on {device}")
    model, _, preprocess = open_clip.create_model_and_transforms(
        MODEL_NAME, pretrained=PRETRAINED
    )
    model.to(device).eval()

    paths = sorted(IMAGES_DIR.glob("*.jpg"))
    print(f"{len(paths)} images to embed")

    uids = []
    embeddings = []
    failures = []

    # images are embedded in batches (not one at a time) because that's much
    # more efficient on both CPU and GPU
    batch_imgs = []
    batch_uids = []

    def flush():
        """Run the current batch through CLIP's image encoder and store the
        resulting vectors, then empty the batch ready for the next one."""
        if not batch_imgs:
            return
        with torch.no_grad():  # we're not training, so skip gradient tracking
            tensor = torch.stack(batch_imgs).to(device)
            feats = model.encode_image(tensor)
            # scale every vector to length 1, so a plain dot product between
            # two embeddings later is the same as their cosine similarity
            feats = feats / feats.norm(dim=-1, keepdim=True)
        embeddings.append(feats.cpu().numpy())
        uids.extend(batch_uids)
        batch_imgs.clear()
        batch_uids.clear()

    for path in tqdm(paths):
        uid = path.stem  # filename without extension, e.g. "0ENR-0001-..."
        try:
            img = Image.open(path).convert("RGB")
            batch_imgs.append(preprocess(img))  # resize/normalise for CLIP's input
            batch_uids.append(uid)
        except Exception:
            # corrupt/unreadable image file - skip it, don't crash the whole run
            failures.append(uid)
            continue
        if len(batch_imgs) >= BATCH_SIZE:
            flush()
    flush()  # final, possibly-partial batch

    emb_matrix = np.concatenate(embeddings, axis=0).astype("float32")
    np.save(OUT_EMB, emb_matrix)
    OUT_UIDS.write_text(json.dumps(uids))  # same row order as emb_matrix

    print(f"embedded {len(uids)} images -> {OUT_EMB} ({emb_matrix.shape})")
    if failures:
        print(f"{len(failures)} failures")
        pathlib.Path("data/embed_failures.txt").write_text("\n".join(failures))


if __name__ == "__main__":
    main()
