// Locally, Flask serves this page and the API from the same origin, so a
// relative path works. Once this page is hosted separately (GitHub Pages),
// it needs the deployed backend's actual URL instead - set that here once
// it exists.
const API_BASE =
  location.hostname === "localhost" || location.hostname === "127.0.0.1"
    ? ""
    : "https://REPLACE-WITH-CLOUD-RUN-URL";

const form = document.getElementById("search-form");
const queryInput = document.getElementById("query");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const blurbEl = document.getElementById("mode-blurb");

// one explanation per mode, written for a gallery visitor rather than a
// developer - shown as soon as a mode is picked, before any search runs
const BLURBS = {
  clip: `<strong>CLIP</strong> is a machine-learning model trained on hundreds of
    millions of image-and-caption pairs from the internet, learning to place
    pictures and the words that describe them close together in the same
    mathematical space. Because it was trained on whole images, it responds
    to subject matter, composition and style - not just colour. Rather than
    just picking paintings that are close to your search words, this mode
    also checks each painting against a small set of generically opposite
    mood words (so a search for "joyful" is weighed against "sorrowful" and
    similar) - this catches paintings that would otherwise rank well on your
    words alone despite reading, overall, as the opposite.`,
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
  rrf: `This blends the two approaches above using <strong>Reciprocal Rank
    Fusion</strong>, a technique from search-engine research for combining
    rankings that aren't on comparable scales. Rather than averaging raw
    numbers from each method, it looks at each painting's position in both
    the CLIP ranking and the colour ranking, and rewards paintings that rank
    well across both.`,
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

  statusEl.textContent = "Searching…";
  resultsEl.innerHTML = "";

  const url = `${API_BASE}/api/search?q=${encodeURIComponent(query)}&mode=${mode}`;
  let data;
  try {
    const resp = await fetch(url);
    data = await resp.json();
  } catch (err) {
    statusEl.textContent = "Something went wrong reaching the search API.";
    return;
  }

  if (!data.results || data.results.length === 0) {
    statusEl.textContent = "No results.";
    return;
  }

  statusEl.textContent = `${data.results.length} results · ${data.score_label}`;
  resultsEl.innerHTML = data.results.map(renderCard).join("");
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
