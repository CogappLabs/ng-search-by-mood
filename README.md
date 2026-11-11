# ng-emotion-search

Exploring emotion-based discovery over the National Gallery collection (via the
`ng-hack-apps` API), for Cogapp's hackday.

Does **not** use the API's own `clip_moods`/`haiku_moods` fields by choice — we're
building our own embedding-based pipeline instead. We do reuse the API's colour
swatch data (lightness/chroma/hue), since that's colourimetry, not a mood judgment.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in the real `NG_API_USER` / `NG_API_PASS`
(ask in the team channel if you don't have them) - `.env` is gitignored, so
these never end up in source control. This is only needed to run the
precompute scripts below (`fetch_metadata.py` etc.) - the deployed search API
itself (`app.py`) never calls the National Gallery hack API directly, so it
doesn't need these credentials at all.

## Pipeline

Run in order:

1. `python fetch_metadata.py` — paginate `/api/paintings?has_image=true`, dump
   raw metadata (incl. colour swatches) to `data/paintings_raw.jsonl`.
2. `python colour_features.py` — derive a continuous weighted lightness/chroma/hue
   per painting from the swatches, no image download needed. Writes
   `data/colour_features.parquet`.
3. `python download_images.py` — download each painting's IIIF image (≤800px,
   public, no auth) to `data/images/<uid>.jpg`. Resumable (skips existing files).
4. `python embed_images.py` — run every downloaded image through CLIP
   (`ViT-B-32`/openai, local, no API key) to get a 512-d embedding per painting.
   Writes `data/clip_embeddings.npy` + `data/clip_uids.json` (same row order).

`data/` is gitignored (regenerate by re-running the pipeline).

5. `python colour_vad.py` — derive a colour-only valence/arousal/dominance
   score per painting (Valdez & Mehrabian's brightness/saturation formulas),
   rescaled to the lexicon's -1..+1 range. Writes `data/colour_vad.parquet`.
   Independent of CLIP entirely - no images touched.
6. Download the [NRC-VAD Lexicon v2.1](http://saifmohammad.com/WebPages/nrc-vad.html)
   (non-commercial/research use) and unzip it to
   `data/lexicons/nrc-vad-v2.1/NRC-VAD-Lexicon-v2.1/` - `vad_lexicon.py` reads
   `NRC-VAD-Lexicon-v2.1.txt` from there.

## Three independent search modes

- `clip_rank.rank_uids(query)` / `rank_with_scores(query)` - CLIP cosine
  similarity (sees the whole image: subject, style, everything).
- `vad_rank.rank_uids(query)` / `rank_with_scores(query)` - NRC-VAD lexicon
  distance against colour-derived valence/arousal/dominance (colour only,
  no subject matter). Intensity modifiers ("very", "slightly", and "mild"/
  "mildly" as deliberate synonyms of "slightly") scale the lexicon score via
  VADER's booster/dampener logic - see `vad_lexicon.py`.
- `rrf_search.fuse(query)` - combines the two via Reciprocal Rank Fusion
  (rank-based, not score-based, since CLIP similarity and VAD distance aren't
  on comparable scales).

Each is kept deliberately separate (not merged into one scoring function) so
the interface can offer all three as distinct modes rather than just the
fused one.

## Web interface

```bash
python app.py  # http://localhost:5050
```

A single search box with a CLIP / colour-VAD / fused (RRF) mode selector,
calling `/api/search?q=...&mode=clip|vad|rrf`. Frontend is plain HTML/CSS/JS
in `static/` (no build step). First query in each mode is a bit slower
(loading the CLIP model/lexicon into memory); subsequent queries are fast.

## Licensing note

Images are © The National Gallery, London, CC BY-NC-ND 4.0: "show them whole and
unaltered: no cropping, tinting or overlays" — that restriction is about *display*,
not analysis, but keep it in mind when we get to the actual interface.
