// JS port of clip_rank.py - CLIP's text encoder runs IN THE BROWSER (via
// Hugging Face Transformers.js/ONNX), but only ever embeds the one short
// string a visitor types. All 2558 painting IMAGE embeddings were already
// computed once in Python and are just fetched here as static data - see
// export_web_data.py and README.md for why this split is possible at all.
//
// Known limitation (recorded in MILESTONES.md): this ONNX model and the
// open_clip model used to precompute the image embeddings are two different
// implementations of "the same" checkpoint, so results are thematically
// similar but not numerically identical to the Python pipeline's.

import { scoreQuery } from "./vad-lexicon.js";

const MODEL_ID = "Xenova/clip-vit-base-patch32";
const D = 512; // embedding dimension for this model

let _tokenizer = null;
let _textModel = null;
let _embeddings = null; // Float32Array, row-major (uid i at offset i*D)
let _uids = null;
let _anchorVecs = null; // {"valence": {"pos": [...], "neg": [...]}, ...}

async function load() {
  if (_embeddings) return;

  const [{ AutoTokenizer, CLIPTextModelWithProjection }, embBuf, uids, anchors] =
    await Promise.all([
      import("https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.2.0"),
      fetch("data/embeddings.bin").then((r) => r.arrayBuffer()),
      fetch("data/uids.json").then((r) => r.json()),
      fetch("data/anchor_vectors.json").then((r) => r.json()),
    ]);

  _tokenizer = await AutoTokenizer.from_pretrained(MODEL_ID);
  _textModel = await CLIPTextModelWithProjection.from_pretrained(MODEL_ID);
  _embeddings = new Float32Array(embBuf);
  _uids = uids;
  _anchorVecs = anchors;
}

// Run one string through CLIP's text encoder, returning a unit-length
// Float32Array - the JS equivalent of clip_rank.py's _embed_texts().
async function embedText(text) {
  const inputs = await _tokenizer([text], { padding: true, truncation: true });
  const { text_embeds } = await _textModel(inputs);
  const vec = Float32Array.from(text_embeds.data);
  let norm = 0;
  for (let i = 0; i < vec.length; i++) norm += vec[i] * vec[i];
  norm = Math.sqrt(norm);
  for (let i = 0; i < vec.length; i++) vec[i] /= norm;
  return vec;
}

// cosine similarity against every painting at once (both sides are already
// unit-length, so this is just a dot product per row)
function similarityToAll(vec) {
  const n = _uids.length;
  const sims = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    let dot = 0;
    const base = i * D;
    for (let d = 0; d < D; d++) dot += _embeddings[base + d] * vec[d];
    sims[i] = dot;
  }
  return sims;
}

// Returns [[uid, margin], ...] best match first - see clip_rank.py's
// rank_with_scores() for the full reasoning behind the contrastive margin
// and the per-query axis selection. `precomputedVad` lets a caller that
// already called scoreQuery() (e.g. app.js, running all three modes per
// search) skip a redundant lookup - falls back to calling it here if not
// given.
export async function rankWithScores(query, precomputedVad) {
  await load();

  const queryVec = await embedText(query);
  const querySims = similarityToAll(queryVec);

  const { vad, recognized } = precomputedVad ?? (await scoreQuery(query));

  // CLIP's own embedding is meaningful regardless of lexicon coverage
  // (plenty of real, non-nonsense searches - "cathedral", "ship" - aren't
  // emotion words at all), so this mode still returns results either way.
  // But when NOTHING in the query matched the lexicon, there's no real
  // basis for picking which mood axis/pole to contrast against - rather
  // than silently defaulting to an arbitrary one, skip the contrastive
  // margin entirely and fall back to plain CLIP similarity.
  if (!recognized) {
    const scored = _uids.map((uid, i) => [uid, querySims[i]]);
    scored.sort((a, b) => b[1] - a[1]);
    return scored;
  }

  const axes = ["valence", "arousal", "dominance"];
  let dominantAxis = 0;
  for (let i = 1; i < 3; i++) {
    if (Math.abs(vad[i]) > Math.abs(vad[dominantAxis])) dominantAxis = i;
  }
  const axisName = axes[dominantAxis];
  const pole = vad[dominantAxis] >= 0 ? "pos" : "neg";
  const contrastPole = pole === "pos" ? "neg" : "pos";
  const contrastVec = Float32Array.from(_anchorVecs[axisName][contrastPole]);
  const contrastSims = similarityToAll(contrastVec);

  const scored = _uids.map((uid, i) => [uid, querySims[i] - contrastSims[i]]);
  scored.sort((a, b) => b[1] - a[1]);
  return scored;
}

export async function rankUids(query, precomputedVad) {
  return (await rankWithScores(query, precomputedVad)).map(([uid]) => uid);
}
