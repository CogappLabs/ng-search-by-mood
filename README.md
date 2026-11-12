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
7. `python description_vad.py` — derive a valence/arousal/dominance score per
   painting from the National Gallery's own curatorial `short_description`
   text (via the same NRC-VAD lexicon), not the image or its colours. Writes
   `data/description_vad.parquet`. Paintings with no description (~1.3%) are
   skipped rather than scored as neutral.
8. `python export_web_data.py` — reshape everything above into static files
   the browser can fetch directly (`docs/data/`): a flat binary
   `embeddings.bin`, `paintings.json` (display fields only - no raw
   description text, since it's already been pre-scored into numbers), the
   colour/description VAD tables, the lexicon, and the 6 anchor-word vectors
   (precomputed here so the browser never embeds anything except the
   visitor's own query).

## Three independent rankers, fused

- `clip_rank.rank_uids(query)` / `rank_with_scores(query)` - CLIP, contrastive:
  scores a painting by its similarity to the query MINUS its similarity to a
  generic opposite-mood anchor, so a painting that reads as more aligned with
  the opposite of the query doesn't still rank well just by also having some
  similarity to the query in isolation. Which NRC-VAD axis to contrast on
  (valence/arousal/dominance) is picked per query, using whichever axis is
  most extreme for that query's own lexicon score - "joy" is valence-led, but
  "boredom" is arousal-led, so it's contrasted against "exciting"/"thrilling"
  rather than "happy"/"sad".
- `vad_rank.rank_uids(query)` / `rank_with_scores(query)` - NRC-VAD lexicon
  distance against colour-derived valence/arousal/dominance (colour only,
  no subject matter).
- `description_rank.rank_uids(query)` / `rank_with_scores(query)` - NRC-VAD
  lexicon distance against the painting's own curatorial description text -
  catches cases where the image's colour/style reads one way but the known
  subject matter reads another (e.g. a devotional "Man of Sorrows" painting
  scoring moderately well on "joyful" by colour/style alone).

All three share `vad_lexicon.py` for turning a query into a (valence, arousal,
dominance) triple, including intensity modifiers ("very", "slightly", and
"mild"/"mildly" as deliberate synonyms of "slightly") via VADER's
booster/dampener logic.

`rrf_search.fuse(query)` combines any number of these via Reciprocal Rank
Fusion (rank-based, not score-based, since similarity and distance scores
aren't on comparable scales) - defaults to all three. Each ranker is still
kept as its own independent module (not merged into one scoring function) so
the interface can offer each as its own mode, not just the fused one.

## Web interface - fully client-side, no backend

Everything runs in the browser now - `docs/` is the *entire* deployment, and
GitHub Pages can serve it directly with nothing else to host, deploy or pay
for. This only works because CLIP's TEXT encoder (the only part that needs
to run per-query) runs in-browser via Hugging Face's Transformers.js
(`Xenova/clip-vit-base-patch32`, an ONNX port of the same checkpoint
`embed_images.py` uses) - every painting's IMAGE embedding was already
precomputed once in Python and is just fetched as static data
(`docs/data/embeddings.bin`). The VAD-lexicon rankers and RRF fusion involve
no model at all, just arithmetic, and are plain JS ports of their Python
originals:

- `docs/vad-lexicon.js` ↔ `vad_lexicon.py`
- `docs/clip-rank.js` ↔ `clip_rank.py`
- `docs/vad-rank.js` (colour) + `docs/description-rank.js` ↔ `vad_rank.py` / `description_rank.py`
- `docs/rrf.js` ↔ `rrf_search.py`
- `docs/app.js` - wires these together; no more `/api/search`, no `API_BASE`

**Known limitation** (recorded in `MILESTONES.md`): this ONNX model and
`open_clip` (used to precompute the image embeddings) are two different
implementations of "the same" checkpoint, so results are thematically
similar but not numerically identical to the Python pipeline's.

To preview locally, serve `docs/` with any static file server, e.g.
`python -m http.server --directory docs`, or just open `docs/index.html`
via a local server of your choice (not `file://` - the browser needs to
`fetch()` the data files).

`app.py`/`Dockerfile` are no longer part of the deploy path (that was the
Cloud Run/AWS-backed plan before this rewrite) - kept only as the original
server-based reference implementation, not required to run or deploy the
interface.

## Licensing note

Images are © The National Gallery, London, CC BY-NC-ND 4.0: "show them whole and
unaltered: no cropping, tinting or overlays" — that restriction is about *display*,
not analysis, but keep it in mind when we get to the actual interface.
