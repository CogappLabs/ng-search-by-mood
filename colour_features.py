import json
import math
import pathlib

import pandas as pd

IN_PATH = pathlib.Path("data/paintings_raw.jsonl")
OUT_PATH = pathlib.Path("data/colour_features.parquet")


def weighted_lch(swatches):
    """Collapse a painting's list of colour swatches (each with its own
    lightness `l`, chroma `c`, hue `h` and area proportion `prop`) down to one
    overall L/C/H triple for the whole painting, weighted by how much of the
    image each swatch covers.

    L (lightness) and C (chroma) are plain weighted averages. Hue is an angle
    (0-360 degrees), so averaging it directly would be wrong near the 0/360
    wrap-around - e.g. averaging 350 and 10 degrees should give 0, not 180.
    Instead we convert each hue to a 2D point on the unit circle, average
    those points, then convert back to an angle (a "circular mean")."""
    if not swatches:
        return None
    total_w = sum(s["prop"] for s in swatches)
    if total_w == 0:
        return None
    L = sum(s["l"] * s["prop"] for s in swatches) / total_w
    C = sum(s["c"] * s["prop"] for s in swatches) / total_w
    x = sum(math.cos(math.radians(s["h"])) * s["prop"] for s in swatches)
    y = sum(math.sin(math.radians(s["h"])) * s["prop"] for s in swatches)
    H = math.degrees(math.atan2(y, x)) % 360
    return L, C, H


def main():
    rows = []
    with IN_PATH.open() as f:
        for line in f:
            item = json.loads(line)
            lch = weighted_lch(item.get("swatches") or [])
            if lch is None:
                # a handful of paintings have no swatches at all - skip them
                continue
            L, C, H = lch
            rows.append(
                {
                    "uid": item["uid"],
                    "title": item["title"],
                    "maker": item.get("maker"),
                    "lightness": L,
                    "chroma": C,
                    "hue": H,
                    # keep the API's own qualitative bands too, for reference/sanity-checking
                    "tone": (item.get("colour") or {}).get("tone"),
                    "colourfulness": (item.get("colour") or {}).get("colourfulness"),
                    "image_url": (item.get("image") or {}).get("large"),
                }
            )

    df = pd.DataFrame(rows)
    df.to_parquet(OUT_PATH, index=False)
    print(f"{len(df)} paintings with colour features -> {OUT_PATH}")
    print(df[["lightness", "chroma", "hue"]].describe())


if __name__ == "__main__":
    main()
