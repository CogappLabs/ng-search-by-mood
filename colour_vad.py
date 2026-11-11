import pathlib

import pandas as pd

IN_PATH = pathlib.Path("data/colour_features.parquet")
OUT_PATH = pathlib.Path("data/colour_vad.parquet")


def minmax(series):
    """Rescale a column to 0..1 using its own min/max across our collection."""
    return (series - series.min()) / (series.max() - series.min())


def rescale_to_pm1(series):
    """Rescale a column to -1..+1 using its own min/max, so it's on the same
    scale as the NRC-VAD lexicon's -1..+1 scores and can be compared to them."""
    return minmax(series) * 2 - 1


def main():
    df = pd.read_parquet(IN_PATH)

    # Valdez & Mehrabian (1994) found brightness (B) and saturation (S) of a
    # colour predict its perceived valence/arousal/dominance via:
    #   Valence   =  .69*B + .22*S
    #   Arousal   = -.31*B + .60*S
    #   Dominance = -.76*B + .32*S
    # Their B/S were normalised 0..1 stimulus values. Our `lightness` and
    # `chroma` columns are a different colour space (LCH) on a different
    # scale, so we min-max normalise them to 0..1 across our own collection
    # first - this makes "brightest/most saturated painting in the National
    # Gallery" map to B=S=1, not to some absolute reference.
    B = minmax(df["lightness"])
    S = minmax(df["chroma"])

    raw_valence = 0.69 * B + 0.22 * S
    raw_arousal = -0.31 * B + 0.60 * S
    raw_dominance = -0.76 * B + 0.32 * S

    # the formulas above don't naturally centre on 0 (e.g. valence is always
    # >= 0), so rescale each dimension to -1..+1 across our collection, to
    # match the NRC-VAD lexicon's scale for later comparison.
    df["valence"] = rescale_to_pm1(raw_valence)
    df["arousal"] = rescale_to_pm1(raw_arousal)
    df["dominance"] = rescale_to_pm1(raw_dominance)

    out = df[["uid", "title", "maker", "valence", "arousal", "dominance"]]
    out.to_parquet(OUT_PATH, index=False)
    print(f"{len(out)} paintings with colour-derived VAD -> {OUT_PATH}")
    print(out[["valence", "arousal", "dominance"]].describe())


if __name__ == "__main__":
    main()
