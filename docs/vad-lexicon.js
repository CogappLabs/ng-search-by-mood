// JS port of vad_lexicon.py - turns free text into a (valence, arousal,
// dominance) triple, on the same -1..+1 scale as the NRC-VAD lexicon.
// lexicon.json / booster_dict.json are precomputed once in Python (see
// export_web_data.py) and just fetched here, not recomputed.

let _lexicon = null;
let _boosterDict = null;
let _maxModifierWords = null;

async function load() {
  if (_lexicon) return;
  const [lexicon, boosterDict] = await Promise.all([
    fetch("data/lexicon.json").then((r) => r.json()),
    fetch("data/booster_dict.json").then((r) => r.json()),
  ]);
  _lexicon = lexicon;
  _boosterDict = boosterDict;
  // modifier phrases can be 1 or 2 words ("very" vs "kind of") - precompute
  // the longest one so we can try longer matches first, same as the
  // Python version's _MAX_MODIFIER_WORDS
  _maxModifierWords = Math.max(
    ...Object.keys(boosterDict).map((p) => p.split(" ").length)
  );
}

function tokenize(text) {
  return (text.toLowerCase().match(/[a-z']+/g) || []);
}

// Same logic as vad_lexicon.py's score_query(): whole-query exact match
// first, otherwise walk token by token, letting a recognised intensity
// modifier (e.g. "very", "slightly") scale the word right after it instead
// of contributing a score of its own. Returns [valence, arousal, dominance].
export async function scoreQuery(text) {
  await load();

  const key = text.trim().toLowerCase();
  if (key in _lexicon) return _lexicon[key];

  const tokens = tokenize(text);
  const vectors = [];
  let i = 0;
  while (i < tokens.length) {
    let modifier = null; // [phrase, wordCount]
    for (let n = _maxModifierWords; n >= 1; n--) {
      const phrase = tokens.slice(i, i + n).join(" ");
      if (phrase in _boosterDict) {
        modifier = [phrase, n];
        break;
      }
    }

    if (modifier) {
      const [phrase, n] = modifier;
      const increment = _boosterDict[phrase];
      i += n;
      if (i < tokens.length && tokens[i] in _lexicon) {
        const [v, a, d] = _lexicon[tokens[i]];
        const scale = 1 + increment; // >1 amplifies, <1 dampens
        vectors.push([v, a, d].map((x) => Math.max(-1, Math.min(1, x * scale))));
        i += 1;
      }
      continue;
    }

    const word = tokens[i];
    if (word in _lexicon) vectors.push(_lexicon[word]);
    i += 1;
  }

  if (vectors.length === 0) return [0, 0, 0];
  return [0, 1, 2].map(
    (dim) => vectors.reduce((sum, v) => sum + v[dim], 0) / vectors.length
  );
}
