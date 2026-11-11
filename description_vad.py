import json
import pathlib

import pandas as pd

from vad_lexicon import load_lexicon, score_query

IN_PATH = pathlib.Path("data/paintings_raw.jsonl")
OUT_PATH = pathlib.Path("data/description_vad.parquet")


def main():
    lexicon = load_lexicon()
    rows = []

    with IN_PATH.open() as f:
        for line in f:
            item = json.loads(line)
            desc = item.get("short_description")
            if not desc or not desc.strip():
                # ~1.3% of paintings have no curatorial description at all -
                # skip them rather than scoring empty text as neutral (0,0,0),
                # which would be a fabricated score, not a real one
                continue
            valence, arousal, dominance = score_query(desc, lexicon)
            rows.append(
                {
                    "uid": item["uid"],
                    "title": item["title"],
                    "maker": item.get("maker"),
                    "valence": valence,
                    "arousal": arousal,
                    "dominance": dominance,
                }
            )

    df = pd.DataFrame(rows)
    # score_query() already returns values on the NRC-VAD lexicon's native
    # -1..+1 scale (it's a direct average of lexicon entries, unlike colour_vad's
    # formula-derived scores) - no rescaling needed here.
    df.to_parquet(OUT_PATH, index=False)
    print(f"{len(df)} paintings with description-derived VAD -> {OUT_PATH}")
    print(df[["valence", "arousal", "dominance"]].describe())


if __name__ == "__main__":
    main()
