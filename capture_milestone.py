"""Snapshot the top-10 results for a fixed set of words, across all three
search modes, as a markdown section - for tracking how results change across
development milestones (e.g. for a write-up/blog post). Appends to
MILESTONES.md rather than overwriting it, so each run adds a new dated
section on top of whatever's already there.

Usage: python capture_milestone.py "label for this milestone" "diary note - what we noticed and what we changed, briefly"
"""

import json
import sys

import clip_rank
import vad_rank
import rrf_search

WORDS = ["joy", "sorrow", "mild boredom", "frightening"]
TOP_K = 10
OUT_PATH = "MILESTONES.md"


def load_meta():
    meta = {}
    with open("data/paintings_raw.jsonl") as f:
        for line in f:
            item = json.loads(line)
            meta[item["uid"]] = item
    return meta


def render_results(pairs, meta):
    lines = []
    for rank, (uid, score) in enumerate(pairs[:TOP_K], start=1):
        item = meta.get(uid, {})
        title = item.get("title", uid)
        image_url = (item.get("image") or {}).get("large")
        # link the title straight to the image when we have one, so the
        # milestone doc doubles as a quick way to pull up each result later
        title_text = f"[{title}]({image_url})" if image_url else title
        lines.append(
            f"{rank}. **{title_text}** — {item.get('maker', 'Unknown')} "
            f"(score: {score:.4f})"
        )
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(
            'Usage: python capture_milestone.py "label for this milestone" '
            '"diary note (optional)"'
        )
        sys.exit(1)
    label = sys.argv[1]
    note = sys.argv[2] if len(sys.argv) > 2 else None

    meta = load_meta()
    sections = [f"## {label}\n"]
    if note:
        sections.append(f"{note}\n")

    for word in WORDS:
        sections.append(f"### \"{word}\"\n")

        clip_pairs = clip_rank.rank_with_scores(word)
        sections.append("**CLIP (subject & style)**\n")
        sections.append(render_results(clip_pairs, meta) + "\n")

        vad_pairs = vad_rank.rank_with_scores(word)
        sections.append("**VAD (colour mood)**\n")
        sections.append(render_results(vad_pairs, meta) + "\n")

        rrf_order, rrf_scores = rrf_search.fuse(word)
        rrf_pairs = [(uid, rrf_scores[uid]) for uid in rrf_order]
        sections.append("**Combined (RRF)**\n")
        sections.append(render_results(rrf_pairs, meta) + "\n")

    block = "\n".join(sections)
    with open(OUT_PATH, "a") as f:
        f.write(block + "\n")

    print(f"appended '{label}' section to {OUT_PATH}")


if __name__ == "__main__":
    main()
