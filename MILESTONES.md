## Before: plain CLIP similarity (no contrastive margin)

First working build: CLIP, colour-based VAD, and RRF fusion all ranking by raw similarity/distance. Noticed "The Man of Sorrows" (a crucifixion scene) in the fused top 5 for "joy" - CLIP's raw similarity to "joyful" was fairly high in isolation despite the painting being unambiguously sorrowful. That's what led to the next change.

### "joy"

**CLIP (subject & style)**

1. **[An Adoring Angel](https://data.ng.ac.uk/media/iiif/01O2-0001-0000-0000/full/!800,800/0/default.jpg)** — Moretto da Brescia (score: 0.2412)
2. **[The Vestal Virgin Tuccia](https://data.ng.ac.uk/media/iiif/01PA-0001-0000-0000/full/!800,800/0/default.jpg)** — Giovanni Battista Moroni (score: 0.2411)
3. **[A Bather](https://data.ng.ac.uk/media/iiif/029Z-0001-0000-0000/full/!800,800/0/default.jpg)** — Pierre-Auguste Renoir (score: 0.2398)
4. **[The Holy Family](https://data.ng.ac.uk/media/iiif/0GF6-0009-0000-0000/full/!800,800/0/default.jpg)** — Luca Signorelli (score: 0.2386)
5. **[A Choir of Angels: From Left Hand Shutter](https://data.ng.ac.uk/media/iiif/01VH-0001-0000-0000/full/!800,800/0/default.jpg)** — Simon Marmion (score: 0.2384)
6. **[The Labours of the Months: October](https://data.ng.ac.uk/media/iiif/0215-0001-0000-0000/full/!800,800/0/default.jpg)** — Italian, Venetian (score: 0.2376)
7. **[Blessing Redeemer](https://data.ng.ac.uk/media/iiif/0TYK-0000-0000-0000/full/!800,800/0/default.jpg)** — Fra Angelico (score: 0.2372)
8. **[Souvenir of a Journey to Coubron](https://data.ng.ac.uk/media/iiif/01MF-0001-0000-0000/full/!800,800/0/default.jpg)** — Camille Corot (score: 0.2369)
9. **[The Nativity](https://data.ng.ac.uk/media/iiif/0DOG-000B-0000-0000/full/!800,800/0/default.jpg)** — Piero della Francesca (score: 0.2367)
10. **[The Virgin and Child with Flowers](https://data.ng.ac.uk/media/iiif/01O3-0001-0000-0000/full/!800,800/0/default.jpg)** — Carlo Dolci (score: 0.2365)

**VAD (colour mood)**

1. **[Saint Mary Magdalene](https://data.ng.ac.uk/media/iiif/01Y1-0001-0000-0000/full/!800,800/0/default.jpg)** — Master of the Palazzo Venezia Madonna (score: 0.4467)
2. **[Sunflowers](https://data.ng.ac.uk/media/iiif/06QG-0009-0000-0000/full/!800,800/0/default.jpg)** — Vincent van Gogh (score: 0.4777)
3. **[Saint Peter Damian](https://data.ng.ac.uk/media/iiif/0T5Y-0000-0000-0000/full/!800,800/0/default.jpg)** — Jacopo di Cione (score: 0.4870)
4. **[Men with an Ox and Cattle by a Pool](https://data.ng.ac.uk/media/iiif/02AB-0001-0000-0000/full/!800,800/0/default.jpg)** — Jan Both (score: 0.4982)
5. **[A Man with a Wreath](https://data.ng.ac.uk/media/iiif/01RL-0001-0000-0000/full/!800,800/0/default.jpg)** — Greco-Roman (score: 0.5167)
6. **[The Baptism of Christ](https://data.ng.ac.uk/media/iiif/02XQ-0001-0000-0000/full/!800,800/0/default.jpg)** — Lorenzo Monaco (score: 0.5230)
7. **[In the Bibémus Quarry](https://data.ng.ac.uk/media/iiif/0VOC-000B-0000-0000/full/!800,800/0/default.jpg)** — Paul Cezanne (score: 0.5310)
8. **[Saint Benedict admitting Saints into the Order](https://data.ng.ac.uk/media/iiif/0BEI-000B-0000-0000/full/!800,800/0/default.jpg)** — Lorenzo Monaco (score: 0.5508)
9. **[Cows at a Pool](https://data.ng.ac.uk/media/iiif/01NT-0001-0000-0000/full/!800,800/0/default.jpg)** — Narcisse-Virgilio Diaz de la Peña (score: 0.5611)
10. **[Spandrel Angels](https://data.ng.ac.uk/media/iiif/02B9-0001-0000-0000/full/!800,800/0/default.jpg)** — Ugolino di Nerio (score: 0.5648)

**Combined (RRF)**

1. **[Sunflowers](https://data.ng.ac.uk/media/iiif/06QG-0009-0000-0000/full/!800,800/0/default.jpg)** — Vincent van Gogh (score: 0.0293)
2. **[Cows at a Pool](https://data.ng.ac.uk/media/iiif/01NT-0001-0000-0000/full/!800,800/0/default.jpg)** — Narcisse-Virgilio Diaz de la Peña (score: 0.0238)
3. **[The Man of Sorrows](https://data.ng.ac.uk/media/iiif/02RB-0001-0000-0000/full/!800,800/0/default.jpg)** — Master of the Borgo Crucifix (Master of the Franciscan Crucifixes) (score: 0.0228)
4. **[Sunset](https://data.ng.ac.uk/media/iiif/03FN-0001-0000-0000/full/!800,800/0/default.jpg)** — Adolphe Monticelli (score: 0.0220)
5. **[Men with an Ox and Cattle by a Pool](https://data.ng.ac.uk/media/iiif/02AB-0001-0000-0000/full/!800,800/0/default.jpg)** — Jan Both (score: 0.0211)
6. **[A Choir of Angels: From Left Hand Shutter](https://data.ng.ac.uk/media/iiif/01VH-0001-0000-0000/full/!800,800/0/default.jpg)** — Simon Marmion (score: 0.0193)
7. **[Saint Mary Magdalene](https://data.ng.ac.uk/media/iiif/01Y1-0001-0000-0000/full/!800,800/0/default.jpg)** — Master of the Palazzo Venezia Madonna (score: 0.0184)
8. **[The Vestal Virgin Tuccia](https://data.ng.ac.uk/media/iiif/01PA-0001-0000-0000/full/!800,800/0/default.jpg)** — Giovanni Battista Moroni (score: 0.0183)
9. **[A Bather](https://data.ng.ac.uk/media/iiif/029Z-0001-0000-0000/full/!800,800/0/default.jpg)** — Pierre-Auguste Renoir (score: 0.0180)
10. **[An Adoring Angel](https://data.ng.ac.uk/media/iiif/01O2-0001-0000-0000/full/!800,800/0/default.jpg)** — Moretto da Brescia (score: 0.0173)

### "sorrow"

**CLIP (subject & style)**

1. **[The Fish Market](https://data.ng.ac.uk/media/iiif/01NR-0001-0000-0000/full/!800,800/0/default.jpg)** — Philippe Rousseau (score: 0.2574)
2. **[The Performing Dog](https://data.ng.ac.uk/media/iiif/01NN-0001-0000-0000/full/!800,800/0/default.jpg)** — John Lewis Brown (score: 0.2561)
3. **[Witches at their Incantations](https://data.ng.ac.uk/media/iiif/031F-0001-0000-0000/full/!800,800/0/default.jpg)** — Salvator Rosa (score: 0.2544)
4. **[The Magdalene Weeping](https://data.ng.ac.uk/media/iiif/0246-0001-0000-0000/full/!800,800/0/default.jpg)** — Master of the Magdalen Legend (score: 0.2528)
5. **[The Interior of a Barn with Two Peasants](https://data.ng.ac.uk/media/iiif/02E8-0001-0000-0000/full/!800,800/0/default.jpg)** — Isack van Ostade (score: 0.2527)
6. **[The Head of Saint John the Baptist](https://data.ng.ac.uk/media/iiif/026M-0001-0000-0000/full/!800,800/0/default.jpg)** — Italian (score: 0.2521)
7. **[A Herdsman with Seven Cows by a River](https://data.ng.ac.uk/media/iiif/02ZH-0001-0000-0000/full/!800,800/0/default.jpg)** — Aelbert Cuyp (score: 0.2507)
8. **[The Lamentation over the Dead Christ](https://data.ng.ac.uk/media/iiif/06PS-0009-0000-0000/full/!800,800/0/default.jpg)** — Rembrandt (score: 0.2504)
9. **[The Wood Gatherer](https://data.ng.ac.uk/media/iiif/0289-0001-0000-0000/full/!800,800/0/default.jpg)** — Camille Corot (score: 0.2489)
10. **[Portrait of a Lady](https://data.ng.ac.uk/media/iiif/02D0-0001-0000-0000/full/!800,800/0/default.jpg)** — Rogier van der Weyden (score: 0.2489)

**VAD (colour mood)**

1. **[Men of the Docks](https://data.ng.ac.uk/media/iiif/067P-0009-0000-0000/full/!800,800/0/default.jpg)** — George Bellows (score: 1.0185)
2. **[Portrait of Philips Lucasz.](https://data.ng.ac.uk/media/iiif/019R-0001-0000-0000/full/!800,800/0/default.jpg)** — Rembrandt (score: 1.0237)
3. **[Manod Slate Tablet](https://data.ng.ac.uk/media/iiif/0N96-000B-0000-0000/full/!800,800/0/default.jpg)** — Jeremy Deller (score: 1.0446)
4. **[The Castle of Muiden in Winter](https://data.ng.ac.uk/media/iiif/01ZH-0001-0000-0000/full/!800,800/0/default.jpg)** — Jan Beerstraaten (score: 1.0450)
5. **[The Museum at Le Havre](https://data.ng.ac.uk/media/iiif/0731-0009-0000-0000/full/!800,800/0/default.jpg)** — Claude Monet (score: 1.0512)
6. **[La Terrasse at Vasouy, The Garden](https://data.ng.ac.uk/media/iiif/02UA-0001-0000-0000/full/!800,800/0/default.jpg)** — Edouard Vuillard (score: 1.0516)
7. **[The Battle of Jemappes](https://data.ng.ac.uk/media/iiif/02K9-0001-0000-0000/full/!800,800/0/default.jpg)** — Emile-Jean-Horace Vernet (score: 1.0593)
8. **[The Gare St-Lazare](https://data.ng.ac.uk/media/iiif/0YT8-000B-0000-0000/full/!800,800/0/default.jpg)** — Claude Monet (score: 1.0654)
9. **[La Terrasse at Vasouy, The Lunch](https://data.ng.ac.uk/media/iiif/02ZB-0001-0000-0000/full/!800,800/0/default.jpg)** — Edouard Vuillard (score: 1.0803)
10. **[Bust Portrait of Andrea Mantegna](https://data.ng.ac.uk/media/iiif/01P2-0001-0000-0000/full/!800,800/0/default.jpg)** — Italian (score: 1.0841)

**Combined (RRF)**

1. **[Water-Lilies, Setting Sun](https://data.ng.ac.uk/media/iiif/02PK-0001-0000-0000/full/!800,800/0/default.jpg)** — Claude Monet (score: 0.0201)
2. **[The Leaning Tree Trunk](https://data.ng.ac.uk/media/iiif/01Y9-0001-0000-0000/full/!800,800/0/default.jpg)** — Camille Corot (score: 0.0194)
3. **[Fishermen carrying a Drowned Man](https://data.ng.ac.uk/media/iiif/02BC-0001-0000-0000/full/!800,800/0/default.jpg)** — Jozef Israëls (score: 0.0186)
4. **[Rising Tide, Coast of Penmarch](https://data.ng.ac.uk/media/iiif/0GPR-0009-0000-0000/full/!800,800/0/default.jpg)** — Louis Duveau (score: 0.0184)
5. **[The Magdalene Weeping](https://data.ng.ac.uk/media/iiif/0246-0001-0000-0000/full/!800,800/0/default.jpg)** — Master of the Magdalen Legend (score: 0.0175)
6. **[Portrait of Hermine Gallia](https://data.ng.ac.uk/media/iiif/02HP-0001-0000-0000/full/!800,800/0/default.jpg)** — Gustav Klimt (score: 0.0173)
7. **[The Archangel Gabriel: Reverse of Left Hand Shutter](https://data.ng.ac.uk/media/iiif/016Q-0001-0000-0000/full/!800,800/0/default.jpg)** — Pieter Coecke van Aalst (score: 0.0172)
8. **[Portrait of a Lady](https://data.ng.ac.uk/media/iiif/02D0-0001-0000-0000/full/!800,800/0/default.jpg)** — Rogier van der Weyden (score: 0.0172)
9. **[The Fish Market](https://data.ng.ac.uk/media/iiif/01NR-0001-0000-0000/full/!800,800/0/default.jpg)** — Philippe Rousseau (score: 0.0169)
10. **[Witches at their Incantations](https://data.ng.ac.uk/media/iiif/031F-0001-0000-0000/full/!800,800/0/default.jpg)** — Salvator Rosa (score: 0.0169)

### "mild boredom"

**CLIP (subject & style)**

1. **[The Toilet of Venus ('The Rokeby Venus')](https://data.ng.ac.uk/media/iiif/0M25-000B-0000-0000/full/!800,800/0/default.jpg)** — Diego Velázquez (score: 0.2327)
2. **[The Performing Dog](https://data.ng.ac.uk/media/iiif/01NN-0001-0000-0000/full/!800,800/0/default.jpg)** — John Lewis Brown (score: 0.2311)
3. **[Beach Scene, Trouville](https://data.ng.ac.uk/media/iiif/03GF-0001-0000-0000/full/!800,800/0/default.jpg)** — Eugène Boudin (score: 0.2301)
4. **[The Leaning Tree Trunk](https://data.ng.ac.uk/media/iiif/01Y9-0001-0000-0000/full/!800,800/0/default.jpg)** — Camille Corot (score: 0.2299)
5. **[Head of a Man in Blue](https://data.ng.ac.uk/media/iiif/0G53-0009-0000-0000/full/!800,800/0/default.jpg)** — Giacomo Francesco Cipper (score: 0.2297)
6. **[Nymphs surprised by Satyrs](https://data.ng.ac.uk/media/iiif/029G-0001-0000-0000/full/!800,800/0/default.jpg)** — Franchoys Wouters (score: 0.2289)
7. **[A Herdsman with Seven Cows by a River](https://data.ng.ac.uk/media/iiif/02ZH-0001-0000-0000/full/!800,800/0/default.jpg)** — Aelbert Cuyp (score: 0.2281)
8. **[A Man holding a Glass and an Old Woman lighting a Pipe](https://data.ng.ac.uk/media/iiif/011C-0001-0000-0000/full/!800,800/0/default.jpg)** — David Teniers the Younger (score: 0.2281)
9. **[Van Gogh's Chair](https://data.ng.ac.uk/media/iiif/0263-0001-0000-0000/full/!800,800/0/default.jpg)** — Vincent van Gogh (score: 0.2275)
10. **[The Baron de Besenval in his Salon](https://data.ng.ac.uk/media/iiif/02LP-0001-0000-0000/full/!800,800/0/default.jpg)** — Henri-Pierre Danloux (score: 0.2274)

**VAD (colour mood)**

1. **[Portrait of Philips Lucasz.](https://data.ng.ac.uk/media/iiif/019R-0001-0000-0000/full/!800,800/0/default.jpg)** — Rembrandt (score: 0.5014)
2. **[Men of the Docks](https://data.ng.ac.uk/media/iiif/067P-0009-0000-0000/full/!800,800/0/default.jpg)** — George Bellows (score: 0.5074)
3. **[La Terrasse at Vasouy, The Garden](https://data.ng.ac.uk/media/iiif/02UA-0001-0000-0000/full/!800,800/0/default.jpg)** — Edouard Vuillard (score: 0.5177)
4. **[The Museum at Le Havre](https://data.ng.ac.uk/media/iiif/0731-0009-0000-0000/full/!800,800/0/default.jpg)** — Claude Monet (score: 0.5183)
5. **[The Battle of Jemappes](https://data.ng.ac.uk/media/iiif/02K9-0001-0000-0000/full/!800,800/0/default.jpg)** — Emile-Jean-Horace Vernet (score: 0.5247)
6. **[Manod Slate Tablet](https://data.ng.ac.uk/media/iiif/0N96-000B-0000-0000/full/!800,800/0/default.jpg)** — Jeremy Deller (score: 0.5447)
7. **[La Terrasse at Vasouy, The Lunch](https://data.ng.ac.uk/media/iiif/02ZB-0001-0000-0000/full/!800,800/0/default.jpg)** — Edouard Vuillard (score: 0.5521)
8. **[Winter Landscape](https://data.ng.ac.uk/media/iiif/07EI-0009-0000-0000/full/!800,800/0/default.jpg)** — Caspar David Friedrich (score: 0.5561)
9. **[The Castle of Muiden in Winter](https://data.ng.ac.uk/media/iiif/01ZH-0001-0000-0000/full/!800,800/0/default.jpg)** — Jan Beerstraaten (score: 0.5562)
10. **[A Shipping Scene with a Dutch Yacht firing a Salute](https://data.ng.ac.uk/media/iiif/0MG4-000A-0000-0000/full/!800,800/0/default.jpg)** — Jan van de Cappelle (score: 0.5729)

**Combined (RRF)**

1. **[The Leaning Tree Trunk](https://data.ng.ac.uk/media/iiif/01Y9-0001-0000-0000/full/!800,800/0/default.jpg)** — Camille Corot (score: 0.0227)
2. **[A Wagon in the Plains of Artois](https://data.ng.ac.uk/media/iiif/0QH2-000A-0000-0000/full/!800,800/0/default.jpg)** — Camille Corot (score: 0.0197)
3. **[The Toilet of Venus ('The Rokeby Venus')](https://data.ng.ac.uk/media/iiif/0M25-000B-0000-0000/full/!800,800/0/default.jpg)** — Diego Velázquez (score: 0.0185)
4. **[Ballet Dancers](https://data.ng.ac.uk/media/iiif/0IU4-000B-0000-0000/full/!800,800/0/default.jpg)** — Edgar Degas (score: 0.0184)
5. **[Don Quixote and Sancho Panza](https://data.ng.ac.uk/media/iiif/0MAZ-000B-0000-0000/full/!800,800/0/default.jpg)** — Honoré-Victorin Daumier (score: 0.0184)
6. **[Beach Scene, Trouville](https://data.ng.ac.uk/media/iiif/03GF-0001-0000-0000/full/!800,800/0/default.jpg)** — Eugène Boudin (score: 0.0183)
7. **[La Terrasse at Vasouy, The Garden](https://data.ng.ac.uk/media/iiif/02UA-0001-0000-0000/full/!800,800/0/default.jpg)** — Edouard Vuillard (score: 0.0173)
8. **[Men of the Docks](https://data.ng.ac.uk/media/iiif/067P-0009-0000-0000/full/!800,800/0/default.jpg)** — George Bellows (score: 0.0171)
9. **[Portrait of Philips Lucasz.](https://data.ng.ac.uk/media/iiif/019R-0001-0000-0000/full/!800,800/0/default.jpg)** — Rembrandt (score: 0.0169)
10. **[The Performing Dog](https://data.ng.ac.uk/media/iiif/01NN-0001-0000-0000/full/!800,800/0/default.jpg)** — John Lewis Brown (score: 0.0168)

### "frightening"

**CLIP (subject & style)**

1. **[An Old Woman ('The Ugly Duchess')](https://data.ng.ac.uk/media/iiif/0DOM-000B-0000-0000/full/!800,800/0/default.jpg)** — Quinten Massys (score: 0.2574)
2. **[Young Man holding a Skull (Vanitas)](https://data.ng.ac.uk/media/iiif/0LG2-000A-0000-0000/full/!800,800/0/default.jpg)** — Frans Hals (score: 0.2412)
3. **[The Head of Saint John the Baptist](https://data.ng.ac.uk/media/iiif/026M-0001-0000-0000/full/!800,800/0/default.jpg)** — Italian (score: 0.2403)
4. **[Head of a Man in Blue](https://data.ng.ac.uk/media/iiif/0G53-0009-0000-0000/full/!800,800/0/default.jpg)** — Giacomo Francesco Cipper (score: 0.2358)
5. **[A Boy and a Girl with a Cat and an Eel](https://data.ng.ac.uk/media/iiif/03SP-0001-0000-0000/full/!800,800/0/default.jpg)** — Judith Leyster (score: 0.2351)
6. **[A Scene from 'The Forcibly Bewitched'](https://data.ng.ac.uk/media/iiif/01JO-0001-0000-0000/full/!800,800/0/default.jpg)** — Francisco de Goya (score: 0.2351)
7. **[Landscape with Ploughman](https://data.ng.ac.uk/media/iiif/0Q4F-000A-0000-0000/full/!800,800/0/default.jpg)** — Vincent van Gogh (score: 0.2343)
8. **[Head of an Angel](https://data.ng.ac.uk/media/iiif/021V-0001-0000-0000/full/!800,800/0/default.jpg)** — Correggio (score: 0.2330)
9. **[Two Followers of Cadmus devoured by a Dragon](https://data.ng.ac.uk/media/iiif/01Z5-0001-0000-0000/full/!800,800/0/default.jpg)** — Cornelis van Haarlem (score: 0.2312)
10. **[Lake Keitele](https://data.ng.ac.uk/media/iiif/0FH8-0009-0000-0000/full/!800,800/0/default.jpg)** — Akseli Gallen-Kallela (score: 0.2303)

**VAD (colour mood)**

1. **[Subject Composition](https://data.ng.ac.uk/media/iiif/03AQ-0001-0000-0000/full/!800,800/0/default.jpg)** — Adolphe Monticelli (score: 1.2486)
2. **[The Virgin and Child](https://data.ng.ac.uk/media/iiif/0P56-000B-0000-0000/full/!800,800/0/default.jpg)** — Jean Bellegambe (score: 1.2487)
3. **[A Rocky Landscape with an Ox-cart](https://data.ng.ac.uk/media/iiif/01M9-0001-0000-0000/full/!800,800/0/default.jpg)** — Jan Both (score: 1.2487)
4. **[The Dormition of the Virgin](https://data.ng.ac.uk/media/iiif/0G9I-0009-0000-0000/full/!800,800/0/default.jpg)** — Master of the Stams Crucifixion (score: 1.2488)
5. **[Francesco Albani (?)](https://data.ng.ac.uk/media/iiif/0232-0001-0000-0000/full/!800,800/0/default.jpg)** — Giovanni Cariani (score: 1.2488)
6. **[Flowers in a Vase](https://data.ng.ac.uk/media/iiif/0ZVQ-0009-0000-0000/full/!800,800/0/default.jpg)** — Paulus Theodorus van Brussel (score: 1.2489)
7. **[Saint Peter Martyr and a Bishop Saint (Saint Evasio?)](https://data.ng.ac.uk/media/iiif/023B-0001-0000-0000/full/!800,800/0/default.jpg)** — Giovanni Martino Spanzotti (score: 1.2490)
8. **[Still Life: Pewter and Silver Vessels and a Crab](https://data.ng.ac.uk/media/iiif/0316-0001-0000-0000/full/!800,800/0/default.jpg)** — Willem Claesz. Heda (score: 1.2490)
9. **[The Rape of the Sabines (before the signal)](https://data.ng.ac.uk/media/iiif/01UO-0001-0000-0000/full/!800,800/0/default.jpg)** — Domenico Morone (score: 1.2491)
10. **[The Virgin and Child](https://data.ng.ac.uk/media/iiif/0GXN-000B-0000-0000/full/!800,800/0/default.jpg)** — Masaccio (score: 1.2492)

**Combined (RRF)**

1. **[Young Man holding a Skull (Vanitas)](https://data.ng.ac.uk/media/iiif/0LG2-000A-0000-0000/full/!800,800/0/default.jpg)** — Frans Hals (score: 0.0232)
2. **[Subject Composition](https://data.ng.ac.uk/media/iiif/03AQ-0001-0000-0000/full/!800,800/0/default.jpg)** — Adolphe Monticelli (score: 0.0212)
3. **[Portrait of a girl from the Habsburg family](https://data.ng.ac.uk/media/iiif/0JVQ-0009-0000-0000/full/!800,800/0/default.jpg)** — Jakob Seisenegger (score: 0.0184)
4. **[An Old Woman ('The Ugly Duchess')](https://data.ng.ac.uk/media/iiif/0DOM-000B-0000-0000/full/!800,800/0/default.jpg)** — Quinten Massys (score: 0.0177)
5. **[Common with Stormy Sunset](https://data.ng.ac.uk/media/iiif/01HF-0001-0000-0000/full/!800,800/0/default.jpg)** — Narcisse-Virgilio Diaz de la Peña (score: 0.0174)
6. **[Group of Heads](https://data.ng.ac.uk/media/iiif/00TN-0001-0000-0000/full/!800,800/0/default.jpg)** — Correggio (score: 0.0167)
7. **[The Virgin and Child](https://data.ng.ac.uk/media/iiif/0P56-000B-0000-0000/full/!800,800/0/default.jpg)** — Jean Bellegambe (score: 0.0165)
8. **[The Head of Saint John the Baptist](https://data.ng.ac.uk/media/iiif/026M-0001-0000-0000/full/!800,800/0/default.jpg)** — Italian (score: 0.0165)
9. **[A Rocky Landscape with an Ox-cart](https://data.ng.ac.uk/media/iiif/01M9-0001-0000-0000/full/!800,800/0/default.jpg)** — Jan Both (score: 0.0165)
10. **[Francesco Albani (?)](https://data.ng.ac.uk/media/iiif/0232-0001-0000-0000/full/!800,800/0/default.jpg)** — Giovanni Cariani (score: 0.0164)

## After: CLIP contrastive margin (vs opposite-mood anchors)

Change: CLIP mode now scores a contrastive margin - similarity to the query minus similarity to a small set of generically opposite-mood anchor words (e.g. "sorrowful"/"sad" for a positive query), chosen automatically from the query's NRC-VAD valence sign. Result: "The Man of Sorrows" dropped from the fused top 5 to rank 562/2558 for "joy", and "sorrow" became noticeably more thematically coherent (Lamentation, Pietà, Entombment, Agony in the Garden). But "mild boredom" revealed a new limitation: being valence-negative, it's contrasted against positive anchors, which also rewards anything strongly un-happy - including dramatic/violent scenes that aren't boring, just not joyful. VAD's colour-only results are untouched, as expected (identical to the section above).

### "joy"

**CLIP (subject & style)**

1. **[The Virgin and Child with a Shoot of Olive](https://data.ng.ac.uk/media/iiif/02B0-0001-0000-0000/full/!800,800/0/default.jpg)** — Andrea Previtali (score: 0.0268)
2. **[The Virgin and Child](https://data.ng.ac.uk/media/iiif/06ZU-0009-0000-0000/full/!800,800/0/default.jpg)** — Lorenzo di Credi (score: 0.0258)
3. **[The Virgin and Child with Four Angels](https://data.ng.ac.uk/media/iiif/02ZV-0001-0000-0000/full/!800,800/0/default.jpg)** — Ugolino di Nerio (score: 0.0245)
4. **[The Virgin and Child](https://data.ng.ac.uk/media/iiif/01XV-0001-0000-0000/full/!800,800/0/default.jpg)** — Bernardino Luini (score: 0.0233)
5. **[The Virgin and Child with Saints](https://data.ng.ac.uk/media/iiif/0F4F-0009-0000-0000/full/!800,800/0/default.jpg)** — Giovanni Martini da Udine (score: 0.0232)
6. **[The Madonna and Child](https://data.ng.ac.uk/media/iiif/00T5-0001-0000-0000/full/!800,800/0/default.jpg)** — Giovanni Antonio Sogliani (score: 0.0231)
7. **[The Virgin and Child](https://data.ng.ac.uk/media/iiif/030B-0001-0000-0000/full/!800,800/0/default.jpg)** — Italian, Florentine (score: 0.0231)
8. **[The Quaratesi Madonna](https://data.ng.ac.uk/media/iiif/0T8H-0000-0000-0000/full/!800,800/0/default.jpg)** — Gentile da Fabriano (score: 0.0230)
9. **[The Virgin and Child](https://data.ng.ac.uk/media/iiif/0GXN-000B-0000-0000/full/!800,800/0/default.jpg)** — Masaccio (score: 0.0229)
10. **[The Virgin and Child](https://data.ng.ac.uk/media/iiif/01RW-0001-0000-0000/full/!800,800/0/default.jpg)** — Marco d'Oggiono (score: 0.0228)

**VAD (colour mood)**

1. **[Saint Mary Magdalene](https://data.ng.ac.uk/media/iiif/01Y1-0001-0000-0000/full/!800,800/0/default.jpg)** — Master of the Palazzo Venezia Madonna (score: 0.4467)
2. **[Sunflowers](https://data.ng.ac.uk/media/iiif/06QG-0009-0000-0000/full/!800,800/0/default.jpg)** — Vincent van Gogh (score: 0.4777)
3. **[Saint Peter Damian](https://data.ng.ac.uk/media/iiif/0T5Y-0000-0000-0000/full/!800,800/0/default.jpg)** — Jacopo di Cione (score: 0.4870)
4. **[Men with an Ox and Cattle by a Pool](https://data.ng.ac.uk/media/iiif/02AB-0001-0000-0000/full/!800,800/0/default.jpg)** — Jan Both (score: 0.4982)
5. **[A Man with a Wreath](https://data.ng.ac.uk/media/iiif/01RL-0001-0000-0000/full/!800,800/0/default.jpg)** — Greco-Roman (score: 0.5167)
6. **[The Baptism of Christ](https://data.ng.ac.uk/media/iiif/02XQ-0001-0000-0000/full/!800,800/0/default.jpg)** — Lorenzo Monaco (score: 0.5230)
7. **[In the Bibémus Quarry](https://data.ng.ac.uk/media/iiif/0VOC-000B-0000-0000/full/!800,800/0/default.jpg)** — Paul Cezanne (score: 0.5310)
8. **[Saint Benedict admitting Saints into the Order](https://data.ng.ac.uk/media/iiif/0BEI-000B-0000-0000/full/!800,800/0/default.jpg)** — Lorenzo Monaco (score: 0.5508)
9. **[Cows at a Pool](https://data.ng.ac.uk/media/iiif/01NT-0001-0000-0000/full/!800,800/0/default.jpg)** — Narcisse-Virgilio Diaz de la Peña (score: 0.5611)
10. **[Spandrel Angels](https://data.ng.ac.uk/media/iiif/02B9-0001-0000-0000/full/!800,800/0/default.jpg)** — Ugolino di Nerio (score: 0.5648)

**Combined (RRF)**

1. **[Sunflowers](https://data.ng.ac.uk/media/iiif/06QG-0009-0000-0000/full/!800,800/0/default.jpg)** — Vincent van Gogh (score: 0.0203)
2. **[Saint Mary Magdalene](https://data.ng.ac.uk/media/iiif/01Y1-0001-0000-0000/full/!800,800/0/default.jpg)** — Master of the Palazzo Venezia Madonna (score: 0.0197)
3. **[The Assumption of the Virgin](https://data.ng.ac.uk/media/iiif/01RG-0001-0000-0000/full/!800,800/0/default.jpg)** — Matteo di Giovanni (score: 0.0196)
4. **[The Virgin and Child with Four Angels](https://data.ng.ac.uk/media/iiif/02ZV-0001-0000-0000/full/!800,800/0/default.jpg)** — Ugolino di Nerio (score: 0.0183)
5. **[The Virgin and Child](https://data.ng.ac.uk/media/iiif/06ZU-0009-0000-0000/full/!800,800/0/default.jpg)** — Lorenzo di Credi (score: 0.0181)
6. **[The Virgin and Child](https://data.ng.ac.uk/media/iiif/01V3-0001-0000-0000/full/!800,800/0/default.jpg)** — Dalmatian/Venetian (score: 0.0176)
7. **[The Virgin and Child with a Shoot of Olive](https://data.ng.ac.uk/media/iiif/02B0-0001-0000-0000/full/!800,800/0/default.jpg)** — Andrea Previtali (score: 0.0175)
8. **[Saint Peter Damian](https://data.ng.ac.uk/media/iiif/0T5Y-0000-0000-0000/full/!800,800/0/default.jpg)** — Jacopo di Cione (score: 0.0168)
9. **[The Virgin and Child with Saints](https://data.ng.ac.uk/media/iiif/02DM-0001-0000-0000/full/!800,800/0/default.jpg)** — Italian, Florentine (score: 0.0167)
10. **[The Virgin and Child with Saints](https://data.ng.ac.uk/media/iiif/0F4F-0009-0000-0000/full/!800,800/0/default.jpg)** — Giovanni Martini da Udine (score: 0.0165)

### "sorrow"

**CLIP (subject & style)**

1. **[The Interior of a Barn with Two Peasants](https://data.ng.ac.uk/media/iiif/02E8-0001-0000-0000/full/!800,800/0/default.jpg)** — Isack van Ostade (score: 0.0427)
2. **[The Lamentation over the Dead Christ](https://data.ng.ac.uk/media/iiif/06PS-0009-0000-0000/full/!800,800/0/default.jpg)** — Rembrandt (score: 0.0391)
3. **[The Fish Market](https://data.ng.ac.uk/media/iiif/01NR-0001-0000-0000/full/!800,800/0/default.jpg)** — Philippe Rousseau (score: 0.0382)
4. **[Head of Christ Crucified](https://data.ng.ac.uk/media/iiif/0GYD-0009-0000-0000/full/!800,800/0/default.jpg)** — Master of Liesborn (Johann von Soest?) (score: 0.0372)
5. **[A Trout Stream](https://data.ng.ac.uk/media/iiif/0TBF-0000-0000-0000/full/!800,800/0/default.jpg)** — Philip Reinagle (score: 0.0368)
6. **[Christ carrying his Cross](https://data.ng.ac.uk/media/iiif/01WK-0001-0000-0000/full/!800,800/0/default.jpg)** — Giampietrino (score: 0.0367)
7. **[Cenotaph to the Memory of Sir Joshua Reynolds](https://data.ng.ac.uk/media/iiif/0GEV-0009-0000-0000/full/!800,800/0/default.jpg)** — John Constable (score: 0.0364)
8. **[Pietà](https://data.ng.ac.uk/media/iiif/02WN-0001-0000-0000/full/!800,800/0/default.jpg)** — Rogier van der Weyden (score: 0.0360)
9. **[The Agony in the Garden](https://data.ng.ac.uk/media/iiif/00TH-0001-0000-0000/full/!800,800/0/default.jpg)** — Garofalo (score: 0.0355)
10. **[The Entombment](https://data.ng.ac.uk/media/iiif/00WG-0001-0000-0000/full/!800,800/0/default.jpg)** — Dirk Bouts (score: 0.0342)

**VAD (colour mood)**

1. **[Men of the Docks](https://data.ng.ac.uk/media/iiif/067P-0009-0000-0000/full/!800,800/0/default.jpg)** — George Bellows (score: 1.0185)
2. **[Portrait of Philips Lucasz.](https://data.ng.ac.uk/media/iiif/019R-0001-0000-0000/full/!800,800/0/default.jpg)** — Rembrandt (score: 1.0237)
3. **[Manod Slate Tablet](https://data.ng.ac.uk/media/iiif/0N96-000B-0000-0000/full/!800,800/0/default.jpg)** — Jeremy Deller (score: 1.0446)
4. **[The Castle of Muiden in Winter](https://data.ng.ac.uk/media/iiif/01ZH-0001-0000-0000/full/!800,800/0/default.jpg)** — Jan Beerstraaten (score: 1.0450)
5. **[The Museum at Le Havre](https://data.ng.ac.uk/media/iiif/0731-0009-0000-0000/full/!800,800/0/default.jpg)** — Claude Monet (score: 1.0512)
6. **[La Terrasse at Vasouy, The Garden](https://data.ng.ac.uk/media/iiif/02UA-0001-0000-0000/full/!800,800/0/default.jpg)** — Edouard Vuillard (score: 1.0516)
7. **[The Battle of Jemappes](https://data.ng.ac.uk/media/iiif/02K9-0001-0000-0000/full/!800,800/0/default.jpg)** — Emile-Jean-Horace Vernet (score: 1.0593)
8. **[The Gare St-Lazare](https://data.ng.ac.uk/media/iiif/0YT8-000B-0000-0000/full/!800,800/0/default.jpg)** — Claude Monet (score: 1.0654)
9. **[La Terrasse at Vasouy, The Lunch](https://data.ng.ac.uk/media/iiif/02ZB-0001-0000-0000/full/!800,800/0/default.jpg)** — Edouard Vuillard (score: 1.0803)
10. **[Bust Portrait of Andrea Mantegna](https://data.ng.ac.uk/media/iiif/01P2-0001-0000-0000/full/!800,800/0/default.jpg)** — Italian (score: 1.0841)

**Combined (RRF)**

1. **[Rising Tide, Coast of Penmarch](https://data.ng.ac.uk/media/iiif/0GPR-0009-0000-0000/full/!800,800/0/default.jpg)** — Louis Duveau (score: 0.0213)
2. **[A View of Delft after the Explosion of 1654](https://data.ng.ac.uk/media/iiif/00VT-0001-0000-0000/full/!800,800/0/default.jpg)** — Egbert van der Poel (score: 0.0192)
3. **[Fishermen carrying a Drowned Man](https://data.ng.ac.uk/media/iiif/02BC-0001-0000-0000/full/!800,800/0/default.jpg)** — Jozef Israëls (score: 0.0179)
4. **[The Castle of Muiden in Winter](https://data.ng.ac.uk/media/iiif/01ZH-0001-0000-0000/full/!800,800/0/default.jpg)** — Jan Beerstraaten (score: 0.0177)
5. **[The Interior of a Barn with Two Peasants](https://data.ng.ac.uk/media/iiif/02E8-0001-0000-0000/full/!800,800/0/default.jpg)** — Isack van Ostade (score: 0.0172)
6. **[Men of the Docks](https://data.ng.ac.uk/media/iiif/067P-0009-0000-0000/full/!800,800/0/default.jpg)** — George Bellows (score: 0.0172)
7. **[The Lamentation over the Dead Christ](https://data.ng.ac.uk/media/iiif/06PS-0009-0000-0000/full/!800,800/0/default.jpg)** — Rembrandt (score: 0.0171)
8. **[Bust Portrait of Andrea Mantegna](https://data.ng.ac.uk/media/iiif/01P2-0001-0000-0000/full/!800,800/0/default.jpg)** — Italian (score: 0.0171)
9. **[The Lamentation at the Foot of the Cross](https://data.ng.ac.uk/media/iiif/01UJ-0001-0000-0000/full/!800,800/0/default.jpg)** — Giovanni Domenico Tiepolo (score: 0.0168)
10. **[Portrait of Philips Lucasz.](https://data.ng.ac.uk/media/iiif/019R-0001-0000-0000/full/!800,800/0/default.jpg)** — Rembrandt (score: 0.0166)

### "mild boredom"

**CLIP (subject & style)**

1. **[The Baron de Besenval in his Salon](https://data.ng.ac.uk/media/iiif/02LP-0001-0000-0000/full/!800,800/0/default.jpg)** — Henri-Pierre Danloux (score: 0.0190)
2. **[A Trout Stream](https://data.ng.ac.uk/media/iiif/0TBF-0000-0000-0000/full/!800,800/0/default.jpg)** — Philip Reinagle (score: 0.0133)
3. **[A Dead Soldier](https://data.ng.ac.uk/media/iiif/0279-0001-0000-0000/full/!800,800/0/default.jpg)** — Italian (score: 0.0106)
4. **[Saint Jerome](https://data.ng.ac.uk/media/iiif/0EEF-000B-0000-0000/full/!800,800/0/default.jpg)** — Jusepe de Ribera (score: 0.0098)
5. **[The Toilet of Venus ('The Rokeby Venus')](https://data.ng.ac.uk/media/iiif/0M25-000B-0000-0000/full/!800,800/0/default.jpg)** — Diego Velázquez (score: 0.0081)
6. **[Oedipus and the Sphinx](https://data.ng.ac.uk/media/iiif/026K-0001-0000-0000/full/!800,800/0/default.jpg)** — Jean-Auguste-Dominique Ingres (score: 0.0077)
7. **[Two Followers of Cadmus devoured by a Dragon](https://data.ng.ac.uk/media/iiif/01Z5-0001-0000-0000/full/!800,800/0/default.jpg)** — Cornelis van Haarlem (score: 0.0069)
8. **[Two Tax-Gatherers](https://data.ng.ac.uk/media/iiif/00SL-0001-0000-0000/full/!800,800/0/default.jpg)** — Marinus van Reymerswale (score: 0.0062)
9. **[A Man Reading (Saint Ivo?)](https://data.ng.ac.uk/media/iiif/03H6-0001-0000-0000/full/!800,800/0/default.jpg)** — Rogier van der Weyden (score: 0.0059)
10. **[Van Gogh's Chair](https://data.ng.ac.uk/media/iiif/0263-0001-0000-0000/full/!800,800/0/default.jpg)** — Vincent van Gogh (score: 0.0056)

**VAD (colour mood)**

1. **[Portrait of Philips Lucasz.](https://data.ng.ac.uk/media/iiif/019R-0001-0000-0000/full/!800,800/0/default.jpg)** — Rembrandt (score: 0.5014)
2. **[Men of the Docks](https://data.ng.ac.uk/media/iiif/067P-0009-0000-0000/full/!800,800/0/default.jpg)** — George Bellows (score: 0.5074)
3. **[La Terrasse at Vasouy, The Garden](https://data.ng.ac.uk/media/iiif/02UA-0001-0000-0000/full/!800,800/0/default.jpg)** — Edouard Vuillard (score: 0.5177)
4. **[The Museum at Le Havre](https://data.ng.ac.uk/media/iiif/0731-0009-0000-0000/full/!800,800/0/default.jpg)** — Claude Monet (score: 0.5183)
5. **[The Battle of Jemappes](https://data.ng.ac.uk/media/iiif/02K9-0001-0000-0000/full/!800,800/0/default.jpg)** — Emile-Jean-Horace Vernet (score: 0.5247)
6. **[Manod Slate Tablet](https://data.ng.ac.uk/media/iiif/0N96-000B-0000-0000/full/!800,800/0/default.jpg)** — Jeremy Deller (score: 0.5447)
7. **[La Terrasse at Vasouy, The Lunch](https://data.ng.ac.uk/media/iiif/02ZB-0001-0000-0000/full/!800,800/0/default.jpg)** — Edouard Vuillard (score: 0.5521)
8. **[Winter Landscape](https://data.ng.ac.uk/media/iiif/07EI-0009-0000-0000/full/!800,800/0/default.jpg)** — Caspar David Friedrich (score: 0.5561)
9. **[The Castle of Muiden in Winter](https://data.ng.ac.uk/media/iiif/01ZH-0001-0000-0000/full/!800,800/0/default.jpg)** — Jan Beerstraaten (score: 0.5562)
10. **[A Shipping Scene with a Dutch Yacht firing a Salute](https://data.ng.ac.uk/media/iiif/0MG4-000A-0000-0000/full/!800,800/0/default.jpg)** — Jan van de Cappelle (score: 0.5729)

**Combined (RRF)**

1. **[Don Quixote and Sancho Panza](https://data.ng.ac.uk/media/iiif/0MAZ-000B-0000-0000/full/!800,800/0/default.jpg)** — Honoré-Victorin Daumier (score: 0.0258)
2. **[Men of the Docks](https://data.ng.ac.uk/media/iiif/067P-0009-0000-0000/full/!800,800/0/default.jpg)** — George Bellows (score: 0.0243)
3. **[A View of Delft after the Explosion of 1654](https://data.ng.ac.uk/media/iiif/00VT-0001-0000-0000/full/!800,800/0/default.jpg)** — Egbert van der Poel (score: 0.0211)
4. **[A Battle](https://data.ng.ac.uk/media/iiif/0261-0001-0000-0000/full/!800,800/0/default.jpg)** — Jan van Huchtenburgh (score: 0.0187)
5. **[The Battle of Jemappes](https://data.ng.ac.uk/media/iiif/02K9-0001-0000-0000/full/!800,800/0/default.jpg)** — Emile-Jean-Horace Vernet (score: 0.0176)
6. **[The Toilet of Venus ('The Rokeby Venus')](https://data.ng.ac.uk/media/iiif/0M25-000B-0000-0000/full/!800,800/0/default.jpg)** — Diego Velázquez (score: 0.0175)
7. **[Portrait of Philips Lucasz.](https://data.ng.ac.uk/media/iiif/019R-0001-0000-0000/full/!800,800/0/default.jpg)** — Rembrandt (score: 0.0173)
8. **[The Baron de Besenval in his Salon](https://data.ng.ac.uk/media/iiif/02LP-0001-0000-0000/full/!800,800/0/default.jpg)** — Henri-Pierre Danloux (score: 0.0168)
9. **[La Terrasse at Vasouy, The Garden](https://data.ng.ac.uk/media/iiif/02UA-0001-0000-0000/full/!800,800/0/default.jpg)** — Edouard Vuillard (score: 0.0168)
10. **[A Trout Stream](https://data.ng.ac.uk/media/iiif/0TBF-0000-0000-0000/full/!800,800/0/default.jpg)** — Philip Reinagle (score: 0.0167)

### "frightening"

**CLIP (subject & style)**

1. **[Two Followers of Cadmus devoured by a Dragon](https://data.ng.ac.uk/media/iiif/01Z5-0001-0000-0000/full/!800,800/0/default.jpg)** — Cornelis van Haarlem (score: 0.0211)
2. **[The Head of Saint John the Baptist](https://data.ng.ac.uk/media/iiif/026M-0001-0000-0000/full/!800,800/0/default.jpg)** — Italian (score: 0.0201)
3. **[An Old Woman ('The Ugly Duchess')](https://data.ng.ac.uk/media/iiif/0DOM-000B-0000-0000/full/!800,800/0/default.jpg)** — Quinten Massys (score: 0.0186)
4. **[A Scene from 'The Forcibly Bewitched'](https://data.ng.ac.uk/media/iiif/01JO-0001-0000-0000/full/!800,800/0/default.jpg)** — Francisco de Goya (score: 0.0181)
5. **[Young Man holding a Skull (Vanitas)](https://data.ng.ac.uk/media/iiif/0LG2-000A-0000-0000/full/!800,800/0/default.jpg)** — Frans Hals (score: 0.0152)
6. **[Saint Peter](https://data.ng.ac.uk/media/iiif/01ZB-0001-0000-0000/full/!800,800/0/default.jpg)** — El Greco (score: 0.0151)
7. **[Seated Woman](https://data.ng.ac.uk/media/iiif/020Q-0001-0000-0000/full/!800,800/0/default.jpg)** — Camille Corot (score: 0.0148)
8. **[Still Life: An Allegory of the Vanities of Human Life](https://data.ng.ac.uk/media/iiif/0MR7-000B-0000-0000/full/!800,800/0/default.jpg)** — Harmen Steenwyck (score: 0.0147)
9. **[An Allegory of Prudence](https://data.ng.ac.uk/media/iiif/0LVA-000A-0000-0000/full/!800,800/0/default.jpg)** — Titian (score: 0.0140)
10. **[Three Ships in a Gale](https://data.ng.ac.uk/media/iiif/0184-0001-0000-0000/full/!800,800/0/default.jpg)** — Willem van de Velde (score: 0.0139)

**VAD (colour mood)**

1. **[Subject Composition](https://data.ng.ac.uk/media/iiif/03AQ-0001-0000-0000/full/!800,800/0/default.jpg)** — Adolphe Monticelli (score: 1.2486)
2. **[The Virgin and Child](https://data.ng.ac.uk/media/iiif/0P56-000B-0000-0000/full/!800,800/0/default.jpg)** — Jean Bellegambe (score: 1.2487)
3. **[A Rocky Landscape with an Ox-cart](https://data.ng.ac.uk/media/iiif/01M9-0001-0000-0000/full/!800,800/0/default.jpg)** — Jan Both (score: 1.2487)
4. **[The Dormition of the Virgin](https://data.ng.ac.uk/media/iiif/0G9I-0009-0000-0000/full/!800,800/0/default.jpg)** — Master of the Stams Crucifixion (score: 1.2488)
5. **[Francesco Albani (?)](https://data.ng.ac.uk/media/iiif/0232-0001-0000-0000/full/!800,800/0/default.jpg)** — Giovanni Cariani (score: 1.2488)
6. **[Flowers in a Vase](https://data.ng.ac.uk/media/iiif/0ZVQ-0009-0000-0000/full/!800,800/0/default.jpg)** — Paulus Theodorus van Brussel (score: 1.2489)
7. **[Saint Peter Martyr and a Bishop Saint (Saint Evasio?)](https://data.ng.ac.uk/media/iiif/023B-0001-0000-0000/full/!800,800/0/default.jpg)** — Giovanni Martino Spanzotti (score: 1.2490)
8. **[Still Life: Pewter and Silver Vessels and a Crab](https://data.ng.ac.uk/media/iiif/0316-0001-0000-0000/full/!800,800/0/default.jpg)** — Willem Claesz. Heda (score: 1.2490)
9. **[The Rape of the Sabines (before the signal)](https://data.ng.ac.uk/media/iiif/01UO-0001-0000-0000/full/!800,800/0/default.jpg)** — Domenico Morone (score: 1.2491)
10. **[The Virgin and Child](https://data.ng.ac.uk/media/iiif/0GXN-000B-0000-0000/full/!800,800/0/default.jpg)** — Masaccio (score: 1.2492)

**Combined (RRF)**

1. **[Subject Composition](https://data.ng.ac.uk/media/iiif/03AQ-0001-0000-0000/full/!800,800/0/default.jpg)** — Adolphe Monticelli (score: 0.0231)
2. **[Young Man holding a Skull (Vanitas)](https://data.ng.ac.uk/media/iiif/0LG2-000A-0000-0000/full/!800,800/0/default.jpg)** — Frans Hals (score: 0.0224)
3. **[Cavalry attacking Infantry](https://data.ng.ac.uk/media/iiif/00XT-0001-0000-0000/full/!800,800/0/default.jpg)** — Philips Wouwerman (score: 0.0179)
4. **[Two Followers of Cadmus devoured by a Dragon](https://data.ng.ac.uk/media/iiif/01Z5-0001-0000-0000/full/!800,800/0/default.jpg)** — Cornelis van Haarlem (score: 0.0178)
5. **[An Old Woman ('The Ugly Duchess')](https://data.ng.ac.uk/media/iiif/0DOM-000B-0000-0000/full/!800,800/0/default.jpg)** — Quinten Massys (score: 0.0172)
6. **[Saint Peter Martyr and a Bishop Saint (Saint Evasio?)](https://data.ng.ac.uk/media/iiif/023B-0001-0000-0000/full/!800,800/0/default.jpg)** — Giovanni Martino Spanzotti (score: 0.0171)
7. **[The Head of Saint John the Baptist](https://data.ng.ac.uk/media/iiif/026M-0001-0000-0000/full/!800,800/0/default.jpg)** — Italian (score: 0.0168)
8. **[The Virgin and Child](https://data.ng.ac.uk/media/iiif/0P56-000B-0000-0000/full/!800,800/0/default.jpg)** — Jean Bellegambe (score: 0.0167)
9. **[Saint Peter](https://data.ng.ac.uk/media/iiif/01ZB-0001-0000-0000/full/!800,800/0/default.jpg)** — El Greco (score: 0.0166)
10. **[Francesco Albani (?)](https://data.ng.ac.uk/media/iiif/0232-0001-0000-0000/full/!800,800/0/default.jpg)** — Giovanni Cariani (score: 0.0164)

