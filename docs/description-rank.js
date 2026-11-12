// Same ranker as vad-rank.js, just pointed at the description-derived VAD
// table instead of the colour-derived one - see createVadRanker().
import { createVadRanker } from "./vad-rank.js";

export const { rankWithScores, rankUids } = createVadRanker("data/description_vad.json");
