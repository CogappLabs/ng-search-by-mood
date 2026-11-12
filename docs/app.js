// Fully client-side now - no backend at all. Everything that used to be
// app.py's /api/search endpoint now runs here, in the browser: CLIP's text
// encoder via clip-rank.js, the two VAD-lexicon rankers, and RRF fusion.
// GitHub Pages only ever serves static files; this is one of them.

import * as clipRank from "./clip-rank.js";
import * as vadRank from "./vad-rank.js";
import * as descriptionRank from "./description-rank.js";
import { fuse } from "./rrf.js";

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

function updateBlurb() {
  const mode = form.querySelector('input[name="mode"]:checked').value;
  blurbEl.innerHTML = BLURBS[mode] || "";
}

form.querySelectorAll('input[name="mode"]').forEach((input) => {
  input.addEventListener("change", updateBlurb);
});
updateBlurb(); // show the default mode's blurb on first load

form.addEventListener("submit", (e) => {
  e.preventDefault();
  runSearch();
});

async function runSearch() {
  const query = queryInput.value.trim();
  if (!query) return;
  const mode = form.querySelector('input[name="mode"]:checked').value;

  // first search in a mode is slower here too - loading the model/lexicon/
  // data into the browser, same idea as the old server's first-request cost
  statusEl.textContent = "Searching…";
  resultsEl.innerHTML = "";

  let pairs, scoreLabel;
  try {
    if (mode === "clip") {
      pairs = (await clipRank.rankWithScores(query)).slice(0, RESULTS_PER_PAGE);
      scoreLabel = "CLIP contrastive margin (higher = closer match)";
    } else if (mode === "vad") {
      pairs = (await vadRank.rankWithScores(query)).slice(0, RESULTS_PER_PAGE);
      scoreLabel = "VAD distance (lower = closer match)";
    } else if (mode === "rrf") {
      const { ranked, scores } = await fuse(query, {
        clip: clipRank.rankUids,
        colour: vadRank.rankUids,
        description: descriptionRank.rankUids,
      });
      pairs = ranked.slice(0, RESULTS_PER_PAGE).map((uid) => [uid, scores[uid]]);
      scoreLabel = "fused RRF score - CLIP + colour + description (higher = closer match)";
    } else {
      statusEl.textContent = `Unknown mode '${mode}'`;
      return;
    }
  } catch (err) {
    console.error(err);
    statusEl.textContent = "Something went wrong running the search.";
    return;
  }

  const meta = await loadMeta();
  if (pairs.length === 0) {
    statusEl.textContent = "No results.";
    return;
  }

  statusEl.textContent = `${pairs.length} results · ${scoreLabel}`;
  resultsEl.innerHTML = pairs
    .map(([uid, score]) => renderCard({ ...(meta[uid] || {}), score: score.toFixed(4) }))
    .join("");
}

function renderCard(item) {
  const image = item.image_url
    ? `<img src="${item.image_url}" alt="${escapeHtml(item.title || "")}" loading="lazy" />`
    : "";
  return `
    <div class="card">
      <div class="image-frame">${image}</div>
      <div class="caption">
        <div class="title">${escapeHtml(item.title || "Untitled")}</div>
        <div class="maker">${escapeHtml(item.maker || "Unknown maker")}</div>
        <div class="score">${item.score}</div>
      </div>
    </div>
  `;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
