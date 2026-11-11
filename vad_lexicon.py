import pathlib
import re

from vaderSentiment.vaderSentiment import BOOSTER_DICT as _VADER_BOOSTER_DICT

LEXICON_PATH = pathlib.Path(
    "data/lexicons/nrc-vad-v2.1/NRC-VAD-Lexicon-v2.1/NRC-VAD-Lexicon-v2.1.txt"
)

# VADER's own booster/dampener words (e.g. "very": +0.293, "slightly": -0.293).
# "mild"/"mildly" aren't in VADER's list, but per the user we treat them as
# synonyms of "slightly" (a dampener), not as the standalone NRC-VAD entry for
# "mild" (which carries its own separate "mild weather"-style connotation).
BOOSTER_DICT = dict(_VADER_BOOSTER_DICT)
BOOSTER_DICT["mild"] = BOOSTER_DICT["slight"]
BOOSTER_DICT["mildly"] = BOOSTER_DICT["slightly"]

# some modifiers are two words ("kind of", "sort of") - precompute the set of
# modifier phrases at each word-length so we can try the longest match first
_MODIFIER_BY_LEN = {}
for _phrase in BOOSTER_DICT:
    _n = len(_phrase.split())
    _MODIFIER_BY_LEN.setdefault(_n, set()).add(_phrase)
_MAX_MODIFIER_WORDS = max(_MODIFIER_BY_LEN)


def load_lexicon():
    """Load the NRC-VAD lexicon into a dict: term -> (valence, arousal, dominance),
    each on a -1 (low) to +1 (high) scale. `term` can be a single word or a
    short multi-word phrase - the lexicon file includes both."""
    lexicon = {}
    with LEXICON_PATH.open() as f:
        next(f)  # skip header row
        for line in f:
            term, v, a, d = line.rstrip("\n").split("\t")
            lexicon[term.lower()] = (float(v), float(a), float(d))
    return lexicon


def _tokenize(text):
    return re.findall(r"[a-z']+", text.lower())


def score_query(text, lexicon):
    """Turn a free-text emotion query into one (valence, arousal, dominance)
    triple, in the same -1..+1 space as the lexicon.

    - If the whole query matches a lexicon entry verbatim (the lexicon has
      many ready-made multi-word phrases, not just single words), that's
      used directly.
    - Otherwise, walk the query word by word. A recognised intensity
      modifier (e.g. "very", "slightly") doesn't score anything itself -
      instead it scales the VAD vector of the word immediately after it,
      pushing it further from neutral (a booster, positive increment) or
      pulling it back toward neutral (a dampener, negative increment).
    - Every other recognised word's VAD vector is used as-is.
    - The final result is the plain average of all the (possibly scaled)
      vectors collected above.

    Words not found in the lexicon at all are silently skipped. If nothing
    in the query is recognised, returns neutral (0, 0, 0).
    """
    key = text.strip().lower()
    if key in lexicon:
        return lexicon[key]

    tokens = _tokenize(text)
    vectors = []
    i = 0
    while i < len(tokens):
        # try the longest possible modifier phrase first (so "kind of" beats "kind")
        modifier = None
        for n in range(_MAX_MODIFIER_WORDS, 0, -1):
            phrase = " ".join(tokens[i : i + n])
            if phrase in BOOSTER_DICT:
                modifier = (phrase, n)
                break

        if modifier:
            _, n = modifier
            increment = BOOSTER_DICT[" ".join(tokens[i : i + n])]
            i += n
            if i < len(tokens) and tokens[i] in lexicon:
                v, a, d = lexicon[tokens[i]]
                scale = 1 + increment  # >1 amplifies, <1 dampens
                vectors.append(
                    tuple(max(-1.0, min(1.0, x * scale)) for x in (v, a, d))
                )
                i += 1
            continue

        word = tokens[i]
        if word in lexicon:
            vectors.append(lexicon[word])
        i += 1

    if not vectors:
        return (0.0, 0.0, 0.0)
    n = len(vectors)
    return tuple(sum(v[dim] for v in vectors) / n for dim in range(3))
