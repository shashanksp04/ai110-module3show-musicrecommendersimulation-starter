# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

VibeMixer 0.1, my tiny hybrid recommender that ranks songs from a classroom CSV using both numeric “vibe” and text labels.

---

## 2. Intended Use  

My recommender suggests a top 5 list from a fixed catalog. Each pick comes with a score and a short “because” explanation. I assume I can describe taste with genre, mood, five sliders (energy, valence, danceability, acousticness, tempo), and an optional favorite artist. My model does not learn from past listens. I built it for classroom demos and exploration, not for real customers.

I would not use it for a real streaming product, wellness or therapy advice, fairness audits, copyright decisions, or anything that needs a large, representative music library.

---

## 3. How the Model Works  

I give each song and the user a five number profile: energy, tempo (I stretch BPM to 0 to 1 using the lowest and highest BPM in the catalog), valence, danceability, and acousticness. I compare the user vector to each song vector with cosine similarity. I turn that similarity into a 0 to 1 score. I add separate bonuses if my genre, mood, or artist string exactly matches the song’s (after I normalize case and spaces). The numeric part counts the most. Then I add the genre part, then mood, then a small artist part. Compared to a naive starter, I added this hybrid mix, catalog based tempo scaling, and an optional artist bump so my explanations stay readable.

---

## 4. Data  

My catalog is 21 songs in `data/songs.csv`. Each row has id, title, artist, genre, mood, energy, tempo in BPM, valence, danceability, and acousticness. I have no audio files and no user listening history. Genres include pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip hop, country, classical, metal, reggae, folk, R&B, house, blues, and punk. Moods include happy, chill, intense, relaxed, and several others. Most genres only appear once, so my set is not balanced and cannot stand in for “all music.”

---

## 5. Strengths  

- When labels and sliders both point at rows that exist in my CSV, my top five often match my intuition (e.g. lofi/chill vs high energy pop).  
- My numeric blend picks up energy, dance, and acoustic shape well enough for class experiments.  
- My explanations name matches and feature levels, which makes it easy for me to see why something ranked high or low.  
- My stress profiles in `main.py` produce clearly different top fives, so what I built is easy to demo.

---

## 6. Limitations and Bias  

In my scorer, genre and mood bonuses need a full string match. “Indie pop” does not count as “pop,” so subgenres and synonyms lose easy points. My catalog is tiny, so diversity is weak and some tastes have almost no close examples. If my words and my sliders disagree, label bonuses can still win over cosine (e.g. classical/serene labels with party like numbers). Similar chill tracks in other genres (jazz, ambient) may sit lower than strict lofi/chill rows because the bonus never fires, even when the numbers are close. That can feel narrow or unfair to me when I care about vibe more than tags.

---

## 7. Evaluation  

I ran `python -m src.main` and switched the `user_prefs` block in `src/main.py` for each profile. I saved sample console output under `outputs/` (`chill_lofi.txt`, `deep_intense_rock.txt`, `subgenre_label_trap.txt`, `contradic_genre_vibe.txt`) and compared top 5 lists side by side. My profiles included High Energy Pop, Chill Lofi, Deep Intense Rock, Subgenre label trap (I say “pop” so “indie pop” gets no genre bonus), and Contradictory genre vs vibe (classical/serene labels with club like sliders). I checked whether lists matched declared genre and mood when the catalog had matches, whether numeric shape pulled rankings the right way, and whether edge cases showed rigid exact match rules. Chill Lofi favored lofi/chill rows but left soft jazz/ambient lower when labels differed. Deep Intense Rock put true rock/intense first, but metal could sit under intense pop because wording on mood or genre matters. Subgenre trap kept true pop above Rooftop Lights (indie pop). Contradictory put Moonlight Sonata Redux first despite weaker cosine than dance tracks, because both label bonuses applied. I also ran `pytest` on the small tests in `tests/test_recommender.py`. I did not use a separate accuracy metric; my evaluation was qualitative, with extra notes in `reflection.md`.

---

## 8. Future Work  

- I would add fuzzy or hierarchical genre matching (treat “indie pop” as related to “pop”).  
- I would add a diversity rule so my top five are not five near duplicates on vibe.  
- I would try history or “don’t play this artist again” once I have more than one row per niche.

---

## 9. Personal Reflection  

I learned that a recommender is not one magic score, it is rules I choose (here, cosine plus label bonuses) and those rules have visible tradeoffs. The surprising part was seeing labels beat sliders when they conflicted; it made “hybrid” feel real instead of abstract. Comparing profiles side by side showed me how small catalogs and exact tags create filter bubble lists even when other songs are numerically close. I will look at real apps and wonder what is in the vector, what is in the text match, and what never made it into the data.
