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

## Web interface - fully client-side, no backend (except one tiny Worker)

Everything except a single lexicon lookup runs in the browser - `docs/` is
the deployment, and GitHub Pages can serve it directly with nothing else to
host, deploy or pay for. This works because CLIP's TEXT encoder (the only
part that needs to run per-query) runs in-browser via Hugging Face's
Transformers.js (`Xenova/clip-vit-base-patch32`, an ONNX port of the same
checkpoint `embed_images.py` uses) - every painting's IMAGE embedding was
already precomputed once in Python and is just fetched as static data
(`docs/data/embeddings.bin`). The RRF fusion logic also involves no model,
just arithmetic:

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

### Why one tiny Worker, and not a fully static lexicon lookup

`docs/vad-lexicon.js` turns free text into a (valence, arousal, dominance)
triple by looking it up against the NRC-VAD Lexicon. Every other piece of
data in `docs/data/` is ours (our own CLIP embeddings, our own colour/
description scores) and is fine to ship as a public static file. The
lexicon itself isn't - its licence explicitly says **"Do not redistribute
the data... you may not otherwise permit third parties to use it"** - and a
`docs/data/lexicon.json` that every GitHub Pages visitor's browser
downloads directly would be exactly that.

The old Flask backend (`app.py`) never had this problem, since it kept the
lexicon server-side and only ever returned computed scores. `worker/` is the
smallest possible equivalent for the client-side version: a single
Cloudflare Worker (`worker/src/index.js`) that does the same lookup
`vad_lexicon.py`/the old client-side `vad-lexicon.js` did, but keeps the
dataset server-side and returns only the derived score for whatever text was
sent - never the lexicon. `docs/vad-lexicon.js` now just calls that Worker's
URL instead of loading `lexicon.json` locally; `clip-rank.js` and
`vad-rank.js`/`description-rank.js` are unchanged, since they only ever
called `scoreQuery()`, not the lexicon directly.

To set it up (needed once, regenerate any time `export_web_data.py` is
re-run):

1. `python export_web_data.py` writes the Worker's own copy of the lexicon
   to `worker/src/data/` (gitignored, same reasoning as `data/lexicons/` -
   never committed, regenerate locally instead).
2. `npm install -g wrangler` (Wrangler needs Node 22+), then `wrangler login`
   from a free Cloudflare account - this opens a browser tab to authorise
   the CLI.
3. From `worker/`, run `wrangler deploy`. Copy the resulting
   `*.workers.dev` URL into `docs/vad-lexicon.js`'s `WORKER_URL` constant.

## Licensing note

Images are © The National Gallery, London, CC BY-NC-ND 4.0: "show them whole and
unaltered: no cropping, tinting or overlays" — that restriction is about *display*,
not analysis, but keep it in mind when we get to the actual interface.
