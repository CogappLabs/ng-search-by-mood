import json
import os

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

import clip_rank
import vad_rank
import rrf_search

# "docs" (not "static") so the exact same folder that Flask serves locally is
# also what GitHub Pages serves directly, with nothing duplicated between them
app = Flask(__name__, static_folder="docs", static_url_path="")

# Once split across two origins (GitHub Pages for the frontend, Cloud Run for
# this API), the browser needs CORS headers to allow that cross-origin fetch.
# This is a read-only, no-auth, public-museum-data endpoint - no cookies, no
# write actions - so allowing any origin carries negligible practical risk.
# ALLOWED_ORIGIN can still be set to a specific origin later if preferred.
CORS(app, resources={r"/api/*": {"origins": os.environ.get("ALLOWED_ORIGIN", "*")}})

# uid -> {title, maker, image_url} - built once at startup from the metadata
# we already fetched from the API, so every search mode can attach display
# info without hitting the National Gallery API again
_meta = {}
with open("data/paintings_raw.jsonl") as f:
    for line in f:
        item = json.loads(line)
        _meta[item["uid"]] = {
            "title": item.get("title"),
            "maker": item.get("maker"),
            "image_url": (item.get("image") or {}).get("large"),
        }

RESULTS_PER_PAGE = 24


@app.get("/")
def index():
    return send_from_directory("docs", "index.html")


@app.get("/api/search")
def search():
    query = request.args.get("q", "").strip()
    mode = request.args.get("mode", "clip")
    if not query:
        return jsonify({"results": []})

    # each mode returns (uid, score) pairs, best match first, already sorted -
    # only the score's MEANING differs (similarity vs distance vs fused rank score)
    if mode == "clip":
        pairs = clip_rank.rank_with_scores(query)[:RESULTS_PER_PAGE]
        score_label = "CLIP similarity (higher = closer match)"
    elif mode == "vad":
        pairs = vad_rank.rank_with_scores(query)[:RESULTS_PER_PAGE]
        score_label = "VAD distance (lower = closer match)"
    elif mode == "rrf":
        ranked, scores = rrf_search.fuse(query)
        pairs = [(uid, scores[uid]) for uid in ranked[:RESULTS_PER_PAGE]]
        score_label = "fused RRF score (higher = closer match)"
    else:
        return jsonify({"error": f"unknown mode '{mode}'"}), 400

    results = [
        {"uid": uid, "score": round(score, 4), **_meta.get(uid, {})}
        for uid, score in pairs
    ]
    return jsonify({"results": results, "score_label": score_label})


if __name__ == "__main__":
    # local dev only - in production (Cloud Run) gunicorn runs this module
    # directly and never executes this block; see Dockerfile's CMD
    app.run(debug=True, port=int(os.environ.get("PORT", 5050)))
