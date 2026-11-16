"""Reshape our precomputed data (currently .npy/.parquet/.jsonl/.txt, meant
for Python scripts) into formats a browser can fetch efficiently, for the
fully client-side version of the search (see docs/*.js). Writes everything
into docs/data/ - nothing here is computed fresh, it's all just exporting
what the existing precompute pipeline already produced.

One exception: the NRC-VAD lexicon itself is NOT written into docs/data/,
since its licence forbids redistributing the dataset and anything under
docs/ is served directly by GitHub Pages. Instead it's written into
worker/src/data/, for the Cloudflare Worker (see worker/src/index.js) to
bundle into its own deployment - that Worker only ever returns a derived
score, never the lexicon, so it doesn't redistribute it either. Like
data/lexicons/, worker/src/data/ is gitignored - never committed."""

import json
import pathlib

import numpy as np
import pandas as pd

import clip_rank
from vad_lexicon import load_lexicon, BOOSTER_DICT

OUT_DIR = pathlib.Path("docs/data")
WORKER_DATA_DIR = pathlib.Path("worker/src/data")


def export_embeddings():
    embeddings = np.load("data/clip_embeddings.npy").astype("float32")
    uids = json.loads(open("data/clip_uids.json").read())
    # raw flat float32 bytes, row-major (uid i's 512 floats at offset i*512*4) -
    # far smaller and faster for the browser to parse than JSON would be for
    # a matrix this size
    embeddings.tofile(OUT_DIR / "embeddings.bin")
    (OUT_DIR / "uids.json").write_text(json.dumps(uids))
    print(f"embeddings.bin: {embeddings.shape}, uids.json: {len(uids)} ids")


def export_paintings():
    rows = []
    with open("data/paintings_raw.jsonl") as f:
        for line in f:
            item = json.loads(line)
            rows.append(
                {
                    "uid": item["uid"],
                    "title": item.get("title"),
                    "maker": item.get("maker"),
                    "image_url": (item.get("image") or {}).get("large"),
                    # the API has no direct link to the painting's page on the
                    # NG website, but nationalgallery.org.uk/paintings/<accession>
                    # reliably redirects to it (checked across a random sample +
                    # every painting in the dataset has an accession)
                    "accession": item.get("accession"),
                }
            )
    (OUT_DIR / "paintings.json").write_text(json.dumps(rows))
    print(f"paintings.json: {len(rows)} paintings (display fields only)")


def export_vad_table(parquet_path, out_name):
    df = pd.read_parquet(parquet_path)
    rows = df[["uid", "valence", "arousal", "dominance"]].to_dict(orient="records")
    (OUT_DIR / out_name).write_text(json.dumps(rows))
    print(f"{out_name}: {len(rows)} paintings")


def export_lexicon():
    """Write the lexicon for the Worker to bundle into ITS OWN deployment,
    not for the browser to fetch - see module docstring and
    worker/src/index.js for why that distinction matters."""
    WORKER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    lexicon = load_lexicon()
    (WORKER_DATA_DIR / "lexicon.json").write_text(json.dumps(lexicon))
    print(f"worker/src/data/lexicon.json: {len(lexicon)} terms")

    (WORKER_DATA_DIR / "booster_dict.json").write_text(json.dumps(BOOSTER_DICT))
    print(f"worker/src/data/booster_dict.json: {len(BOOSTER_DICT)} modifier words")


def export_anchor_vectors():
    """Precompute the 6 anchor embeddings ONCE here, so the browser never
    needs to embed anything except the visitor's own query text."""
    clip_rank._load()
    anchors = {
        axis: {pole: clip_rank._anchor_vecs[axis][pole].tolist() for pole in poles}
        for axis, poles in clip_rank.ANCHORS.items()
    }
    (OUT_DIR / "anchor_vectors.json").write_text(json.dumps(anchors))
    print("anchor_vectors.json: 6 vectors (valence/arousal/dominance x pos/neg)")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    export_embeddings()
    export_paintings()
    export_vad_table("data/colour_vad.parquet", "colour_vad.json")
    export_vad_table("data/description_vad.parquet", "description_vad.json")
    export_lexicon()
    export_anchor_vectors()


if __name__ == "__main__":
    main()
