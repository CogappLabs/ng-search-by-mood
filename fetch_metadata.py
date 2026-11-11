import json
import pathlib

from tqdm import tqdm

from common import api_get, iter_paintings

OUT_DIR = pathlib.Path("data")
OUT_PATH = OUT_DIR / "paintings_raw.jsonl"

# Default card fields don't include these - ask for them explicitly.
# Deliberately NOT requesting clip_moods/haiku_moods: we're building our own
# mood pipeline rather than reusing the API's.
FIELDS = [
    "swatches",            # per-swatch L/C/h colour values + proportion
    "subjects",             # cataloguer-assigned subject terms
    "genre_facet",
    "style_facet",
    "short_description",
    "caption",              # machine-written (Claude Haiku) visual description
    "maker_names",
    "room_title",
]


def main():
    OUT_DIR.mkdir(exist_ok=True)

    # ask for just 1 result first, purely to read back the true `total` count
    total = api_get("/paintings", params={"has_image": "true", "per_page": 1})["total"]
    print(f"{total} photographed paintings to fetch")

    # stream straight to disk as newline-delimited JSON (one record per line)
    # rather than building one huge list in memory
    with OUT_PATH.open("w") as f:
        for item in tqdm(
            iter_paintings(fields=FIELDS, has_image="true"), total=total
        ):
            f.write(json.dumps(item) + "\n")

    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
