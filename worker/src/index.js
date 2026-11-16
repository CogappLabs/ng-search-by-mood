// Cloudflare Worker: scores a free-text emotion query against the NRC-VAD
// lexicon and returns ONLY the derived (valence, arousal, dominance)
// triple - never the lexicon itself.
//
// Why this exists at all: the NRC-VAD lexicon's licence explicitly forbids
// redistributing the dataset ("Do not redistribute the data... you may not
// otherwise permit third parties to use it"). The old Flask backend
// (app.py) never violated this - it kept the lexicon server-side and only
// ever returned computed scores. When the rest of the search moved fully
// client-side (see root README.md), shipping the lexicon as a public
// docs/data/lexicon.json for GitHub Pages to serve would have been exactly
// the redistribution the licence prohibits. This Worker is the smallest
// possible way to keep that one piece server-side without needing a full
// backend again: a single stateless lookup, no model, trivial compute.
//
// This is a straight port of vad_lexicon.py's score_query() (and its
// now-retired client-side twin, the old docs/vad-lexicon.js) - see that
// file for the full reasoning behind the modifier-word scaling logic.

import lexicon from "./data/lexicon.json";
import boosterDict from "./data/booster_dict.json";

// modifier phrases can be 1 or 2 words ("very" vs "kind of") - precompute
// the longest one so we try longer matches first, same as the Python
// version's _MAX_MODIFIER_WORDS
const MAX_MODIFIER_WORDS = Math.max(
  ...Object.keys(boosterDict).map((p) => p.split(" ").length)
);

// low-risk, read-only endpoint (no auth, no sensitive data) - allow any
// origin rather than hardcoding the GitHub Pages URL, so local preview
// (python -m http.server etc) works too
const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
};

function tokenize(text) {
  return text.toLowerCase().match(/[a-z']+/g) || [];
}

// Same logic as vad_lexicon.py's score_query(): whole-query exact match
// first, otherwise walk token by token, letting a recognised intensity
// modifier (e.g. "very", "slightly") scale the word right after it instead
// of contributing a score of its own. Returns { vad: [v, a, d], recognized }
// - `recognized` is false only when literally nothing in the query matched
// the lexicon (e.g. gibberish like "hdgjgdjhgd"), as opposed to a real
// phrase where some words just aren't emotion-coded, which still scores
// normally from whichever words DID match. Callers use this to tell "we
// understood this and it happens to land near neutral" apart from "we
// understood nothing at all", rather than silently treating both the same.
function scoreQuery(text) {
  const key = text.trim().toLowerCase();
  if (key in lexicon) return { vad: lexicon[key], recognized: true };

  const tokens = tokenize(text);
  const vectors = [];
  let i = 0;
  while (i < tokens.length) {
    let modifier = null; // [phrase, wordCount]
    for (let n = MAX_MODIFIER_WORDS; n >= 1; n--) {
      const phrase = tokens.slice(i, i + n).join(" ");
      if (phrase in boosterDict) {
        modifier = [phrase, n];
        break;
      }
    }

    if (modifier) {
      const [phrase, n] = modifier;
      const increment = boosterDict[phrase];
      i += n;
      if (i < tokens.length && tokens[i] in lexicon) {
        const [v, a, d] = lexicon[tokens[i]];
        const scale = 1 + increment; // >1 amplifies, <1 dampens
        vectors.push([v, a, d].map((x) => Math.max(-1, Math.min(1, x * scale))));
        i += 1;
      }
      continue;
    }

    const word = tokens[i];
    if (word in lexicon) vectors.push(lexicon[word]);
    i += 1;
  }

  if (vectors.length === 0) return { vad: [0, 0, 0], recognized: false };
  const vad = [0, 1, 2].map(
    (dim) => vectors.reduce((sum, v) => sum + v[dim], 0) / vectors.length
  );
  return { vad, recognized: true };
}

export default {
  async fetch(request) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS_HEADERS });
    }

    const url = new URL(request.url);
    const q = url.searchParams.get("q");
    if (!q) {
      return new Response(JSON.stringify({ error: "missing ?q= query param" }), {
        status: 400,
        headers: { "Content-Type": "application/json", ...CORS_HEADERS },
      });
    }

    const {
      vad: [valence, arousal, dominance],
      recognized,
    } = scoreQuery(q);
    return new Response(JSON.stringify({ valence, arousal, dominance, recognized }), {
      headers: { "Content-Type": "application/json", ...CORS_HEADERS },
    });
  },
};
