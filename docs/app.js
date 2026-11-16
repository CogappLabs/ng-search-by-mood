// Fully client-side now - no backend at all. Everything that used to be
// app.py's /api/search endpoint now runs here, in the browser: CLIP's text
// encoder via clip-rank.js, the two VAD-lexicon rankers, and RRF fusion.
// GitHub Pages only ever serves static files; this is one of them.

import * as clipRank from "./clip-rank.js";
import * as vadRank from "./vad-rank.js";
import * as descriptionRank from "./description-rank.js";
import { fuseOrders } from "./rrf.js";
import { scoreQuery } from "./vad-lexicon.js";

const RESULTS_PER_PAGE = 24;

const form = document.getElementById("search-form");
const queryInput = document.getElementById("query");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const blurbEl = document.getElementById("mode-blurb");

// uid -> {title, maker, image_url}, loaded once and reused across searches
let _meta = null;
async function loadMeta() {
  if (_meta) return _meta;
  const paintings = await fetch("data/paintings.json").then((r) => r.json());
  _meta = Object.fromEntries(paintings.map((p) => [p.uid, p]));
  return _meta;
}

// one explanation per mode, written for a gallery visitor rather than a
// developer - shown as soon as a mode is picked, before any search runs
const BLURBS = {
  clip: `<strong>CLIP</strong> is a machine-learning model trained on hundreds of
    millions of image-and-caption pairs from the internet, learning to place
    pictures and the words that describe them close together in the same
    mathematical space. It runs right here in your browser. Because it was
    trained on whole images, it responds to subject matter, composition and
    style - not just colour. Rather than just picking paintings that are
    close to your search words, this mode also checks each painting against a
    small set of generically opposite mood words - and picks which kind of
    "opposite" fits your search automatically. "Joyful" is mainly about how
    positive or negative something feels, so it's weighed against "sorrowful"
    and similar; but "boredom" is mainly about how calm or exciting something
    feels, so it's weighed against "exciting"/"thrilling" instead - otherwise
    a dramatic, high-energy painting could rank as "not boring" simply for
    not being happy, which isn't the same thing as actually being boring.`,
  vad: `This mode ignores subject matter completely and looks only at colour.
    Each painting's brightness and saturation (from its dominant colour
    swatches) are converted into how pleasant, how calming-or-exciting, and
    how commanding it feels, using formulas from colour-emotion psychology
    research (<strong>Valdez &amp; Mehrabian, 1994</strong>). Your search words are
    looked up in the <strong>NRC-VAD Lexicon</strong>, a dictionary of ~55,000
    English words individually rated by human volunteers on those same three
    qualities - with words like "very" or "slightly" adjusting the intensity.
    Paintings whose colour-based score lands closest to your words' score
    come first.`,
  rrf: `This blends three signals - CLIP, colour, and a third: the National
    Gallery's own curatorial description of each painting, scored through
    the same NRC-VAD Lexicon as your search words - using <strong>Reciprocal
    Rank Fusion</strong>, a technique from search-engine research for
    combining rankings that aren't on comparable scales. Rather than
    averaging raw numbers from each method, it looks at each painting's
    position in all three rankings, and rewards paintings that rank well
    across them.`,
};

// what each mode's score means, shown next to the result count. CLIP's
// label depends on whether the query was recognised: when it wasn't,
// clip-rank.js falls back to plain similarity rather than a contrastive
// margin (see its own comments), and the label says so explicitly rather
// than claiming a margin that wasn't actually computed.
const SCORE_LABELS = {
  clip: (recognized) =>
    recognized
      ? "CLIP contrastive margin (higher = closer match)"
      : "CLIP similarity only - no mood words recognised to contrast against (higher = closer match)",
  vad: () => "VAD distance (lower = closer match)",
  rrf: () => "fused RRF score - CLIP + colour + description (higher = closer match)",
};

// A search runs all three modes at once and keeps every mode's results
// here, so switching modes with the radio buttons just re-renders from
// this cache instead of re-running anything. {query, recognized, clip, vad,
// rrf} - each of clip/vad/rrf is a [[uid, score], ...] list, same shape as
// before. `recognized` is false only when the lexicon matched nothing at
// all in the query (see vad-lexicon.js) - used to show a specific message
// rather than a confident-looking list built on no real signal.
let _lastResults = null;

function updateBlurb() {
  const mode = form.querySelector('input[name="mode"]:checked').value;
  blurbEl.innerHTML = BLURBS[mode] || "";
}

form.querySelectorAll('input[name="mode"]').forEach((input) => {
  input.addEventListener("change", () => {
    updateBlurb();
    renderCachedResults();
  });
});
updateBlurb(); // show the default mode's blurb on first load

form.addEventListener("submit", (e) => {
  e.preventDefault();
  runSearch();
});

async function runSearch() {
  const query = queryInput.value.trim();
  if (!query) return;

  // first search is slower here too - loading the model/lexicon/data into
  // the browser, same idea as the old server's first-request cost
  statusEl.textContent = "Searching…";
  resultsEl.innerHTML = "";

  try {
    // score the query against the lexicon ONCE and pass it to all three
    // rankers below, rather than each of them calling the Worker itself -
    // also gives us `recognized` up front, for the "no real signal" check
    const queryVad = await scoreQuery(query);

    // run CLIP and colour-VAD once each (their own mode's results come
    // straight from these), plus description-VAD (only needed for RRF) -
    // all in parallel, so e.g. CLIP's text encoder only embeds the query once
    const [clipPairs, vadPairs, descUids] = await Promise.all([
      clipRank.rankWithScores(query, queryVad),
      vadRank.rankWithScores(query, queryVad),
      descriptionRank.rankUids(query, queryVad),
    ]);

    // RRF fuses from the orderings just computed above, rather than
    // re-running each ranker a second time. When nothing was recognized,
    // vadPairs/descUids are both already empty (see vad-rank.js), so the
    // cross-ranker intersection below naturally comes out empty too -
    // RRF needs no separate "nothing recognized" check of its own.
    const { ranked, scores } = fuseOrders({
      clip: clipPairs.map(([uid]) => uid),
      colour: vadPairs.map(([uid]) => uid),
      description: descUids,
    });
    const rrfPairs = ranked.map((uid) => [uid, scores[uid]]);

    _lastResults = {
      query,
      recognized: queryVad.recognized,
      clip: clipPairs,
      vad: vadPairs,
      rrf: rrfPairs,
    };
  } catch (err) {
    console.error(err);
    statusEl.textContent = "Something went wrong running the search.";
    _lastResults = null;
    return;
  }

  await renderCachedResults();
}

// Renders whichever mode is currently selected from _lastResults - called
// both right after a search finishes, and whenever the mode is switched.
async function renderCachedResults() {
  if (!_lastResults) return;
  const mode = form.querySelector('input[name="mode"]:checked').value;
  const pairs = _lastResults[mode].slice(0, RESULTS_PER_PAGE);
  const scoreLabel = SCORE_LABELS[mode](_lastResults.recognized);

  if (pairs.length === 0) {
    statusEl.textContent = _lastResults.recognized
      ? "No results."
      : "We didn't recognise any mood words in that search - try a different word or phrase.";
    resultsEl.innerHTML = "";
    return;
  }

  const meta = await loadMeta();
  statusEl.textContent = `${pairs.length} results · ${scoreLabel}`;
  resultsEl.innerHTML = pairs
    .map(([uid, score]) => renderCard({ ...(meta[uid] || {}), score: score.toFixed(4) }))
    .join("");
}

function renderCard(item) {
  const image = item.image_url
    ? `<img src="${item.image_url}" alt="${escapeHtml(item.title || "")}" loading="lazy" />`
    : "";
  // the API doesn't give a direct link to the painting's page on the NG
  // website, but nationalgallery.org.uk/paintings/<accession> reliably
  // redirects to it - open in a new tab so a search doesn't lose its results
  const nglUrl = item.accession
    ? `https://www.nationalgallery.org.uk/paintings/${encodeURIComponent(item.accession)}`
    : null;
  const cardInner = `
    <div class="image-frame">${image}</div>
    <div class="caption">
      <div class="title">${escapeHtml(item.title || "Untitled")}</div>
      <div class="maker">${escapeHtml(item.maker || "Unknown maker")}</div>
      <div class="score">${item.score}</div>
    </div>
  `;
  return nglUrl
    ? `<a class="card" href="${nglUrl}" target="_blank" rel="noopener">${cardInner}</a>`
    : `<div class="card">${cardInner}</div>`;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
