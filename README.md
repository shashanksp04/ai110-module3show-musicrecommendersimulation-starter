# 🎵 Music Recommender Simulation

## Project Summary

I built and explained a small music recommender system for this project.

My goals were to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what my system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

I implemented VibeMixer 0.1: my hybrid scorer reads `data/songs.csv`, blends cosine similarity on energy, catalog scaled tempo, valence, danceability, and acousticness with exact match bonuses for genre, mood, and optional artist, and prints top picks with explanations. I run it with `python -m src.main`, saved sample runs under `outputs/`, and wrote up behavior and bias in `model_card.md` and `reflection.md`.

---

## How The System Works

I learned that products like Spotify or TikTok usually combine several ideas at once. They look at what you already played or skipped, what people with overlapping taste stream, and what is rising in popularity. Many layers also use content: audio analysis, genre tags, mood labels, or embeddings learned from sound and text. Context matters too (workout vs wind down), and the final feed is often a ranked list after business rules, diversity goals, and experiments on millions of users. Training and scoring run on huge pipelines, so the exact blend is opaque to the listener even when the UI shows a simple “Because you liked …” line.

My simulation keeps one clear pipeline from user preferences to a ranked list. Songs come from `data/songs.csv` with genre, mood, and numeric traits (energy, tempo as BPM, valence, danceability, acousticness). I implemented everything in vanilla Python with no ML libraries. Full scoring weights, tie break rules, data flow, and an example profile dict are in `plan.md`.

### Algorithm

1. Prepare the catalog: I load all rows and compute BPM min and max so every song (and the user profile) uses the same min to max scaling for the second dimension of the vibe vector. Component order is fixed: energy, scaled tempo, valence, danceability, acousticness.
2. Build the user vector from the profile dict and normalize the profile’s genre and mood strings (for example strip and case insensitive comparison).
3. For each song: I build its 5D vector, compute cosine similarity between the user vector and the song vector to get a numeric match, set genre_match and mood_match to 1 when labels match the profile and 0 otherwise, then combine into a weighted score (numeric match plus bonuses; optional artist bonus).
4. Output: I sort by score, apply tie breaks (higher cosine, then genre match, then id), and return the top K recommendations.

### User inputs required

I supply a single dictionary in `main.py` (or the same fields could come from a form or CLI). Required: `energy`, `valence`, `danceability`, and `acousticness` as decimals (roughly 0 to 1); `tempo_bpm` as beats per minute; `genre` and `mood` as one string each. Optional: `top_k` (how many results; default if omitted), and `artist` for my same artist bonus. I do not pass catalog song IDs; my taste is whatever numbers and labels I enter.

### Biases and blind spots

- Catalog bias: Only songs in `songs.csv` can appear. Genres, moods, artists, and numeric ranges reflect whoever built that file, not the whole world of music.
- Label bias: Genre and mood are coarse strings. My exact match rule ignores near neighbors (for example “indie pop” vs “pop”) and favors whatever wording appears in the data.
- Feature bias: Five numbers plus two tags are a cartoon of real listening. They can track vibe roughly but miss lyrics, culture, era, social context, and intent that I care about in real apps.
- Weighting bias: My relative weights on cosine vs genre vs mood encode a value judgment (for example “vibe first, labels second”). Different weights would reorder results with no single objectively correct choice.
- User input bias: My self entered sliders and BPM can be inconsistent or unlike any real track; my code still scores faithfully against that input, which may not match how I actually listen.
- No diversity rule: Top K by score can return a cluster of very similar rows unless I add extra rules later.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):
  ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
  ```
2. Install dependencies:
  ```bash
   pip install -r requirements.txt
  ```
3. Run the app:
  ```bash
   python -m src.main
  ```

### Running Tests

I run the tests with:

```bash
pytest
```

I can add more tests in `tests/test_recommender.py`.

---

## Experiments I Tried

I switched the active `user_prefs` block in `src/main.py` and compared top 5 lists. For example:

- Chill Lofi vs High Energy Pop showed opposite energy, tempo, and acoustic shapes plus different label bonuses.
- Deep Intense Rock surfaced my rock/intense row first but still shared high energy bridge tracks with pop profiles.
- Subgenre label trap (“pop” vs indie pop in the catalog) showed how exact genre strings gate the bonus.
- Contradictory genre vs vibe (classical/serene labels with club like numerics) showed label bonuses beating cosine when both tags matched a row.

I saved sample console output under `outputs/` (`chill_lofi.txt`, `deep_intense_rock.txt`, `subgenre_label_trap.txt`, `contradic_genre_vibe.txt`).

---

## Limitations and Bias

My experiments with those saved runs surfaced one clear weakness: my hybrid score treats genre and mood as all or nothing string equality with sizable bonuses, while numeric similarity is a blended cosine over five features. That design pushes results toward whatever wording appears in my catalog, near neighbors such as “indie pop” vs “pop” or “relaxed” vs “chill” get no partial credit, so cross genre but similar vibe tracks can sink even when their features line up well. When my labels and numbers disagree, the label side can still win: a matching classical/serene row outranked high energy dance songs for my contradictory profile, so self reported tags can dominate felt vibe under my current weights. Energy is not modeled as its own gap (it is just one cosine dimension among tempo, valence, danceability, and acousticness), so “how intense” never gets extra emphasis beyond that shared vector. Together, my behavior resembles a taxonomy weighted filter bubble more than a continuous similarity space across musical taste.

---

## 7. `model_card_template.md`

The Module 3 guidance used a model card outline like the block below. I followed that structure in my own `model_card.md`.

```markdown
# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

```

---

## Reflection on engineering process

### Biggest learning moment

The moment that stuck with me was running the contradictory profile: I entered a detailike a club track, and the list still put the matching classical row on top. I had assumed the numbers would always drag the ranking toward dance and house. Instead I saw in one run that the weights I chose meant tags could override the vector. That turned "hybrid scoring" from a bullet point in a plan into something I could explain to someone else with a concrete example.

### AI tools: help and double checks

Cursor was great for drafting my model card and README, suggesting how to phrase tradeoffs, and keeping the writeups aligned with what the code actually does. I still had to open `recommender.py`, reread the weights, and run `python -m src.main` with different `user_prefs` blocks to make sure the story matched the terminal output. Any time a summary sounded too neat, I checked it against the CSV and the saved `outputs/` files. The tools sped up wording; they did not replace running the program.

### Why simple algorithms still "feel" like recommendations

Even with only cosine similarity and a few binary bonuses, the top five changed in ways that felt intentional when I switched profiles. The printed "Because" lines gave a story for each row, so my brain read intent into what is really arithmetic on five numbers and two strings. I was surprised how little machinery you need before the output stops looking like a random sort and starts feeling like something tuned to "me," as long as the catalog is small enough to eyeball.

### What I would try next

If I extended the project, I would try fuzzy or hierarchical genre matching so indie pop gets partial credit toward pop, and I would add a diversity rule so the top five cannot be five nearly identical vibes. After that I might log scores to a simple spreadsheet and compare profiles quantitatively instead of only reading the console. Those steps would keep the core idea the same but move it closer to how I would iterate on a real prototype.
