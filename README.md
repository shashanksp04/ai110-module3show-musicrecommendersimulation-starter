# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Products like Spotify or TikTok usually combine several ideas at once. They look at what you already played or skipped, what people with overlapping taste stream, and what is rising in popularity. Many layers also use **content**: audio analysis, genre tags, mood labels, or embeddings learned from sound and text. Context matters too (workout vs wind-down), and the final feed is often a ranked list after business rules, diversity goals, and experiments on millions of users. Training and scoring run on huge pipelines, so the exact blend is opaque to the listener even when the UI shows a simple “Because you liked …” line.

This simulation keeps one clear pipeline from user preferences to a ranked list. Songs come from `data/songs.csv` with **genre**, **mood**, and numeric traits (**energy**, **tempo** as BPM, **valence**, **danceability**, **acousticness**). Everything runs in vanilla Python with no ML libraries. Full scoring weights, tie-break rules, data flow, and an example profile dict are in `plan.md`.

### Algorithm

1. **Prepare the catalog:** Load all rows and compute **BPM min and max** so every song (and the user) uses the same min–max scaling for the second dimension of the vibe vector. Component order is fixed: energy, scaled tempo, valence, danceability, acousticness.
2. **Build the user vector** from the profile dict and **normalize** the profile’s genre and mood strings (for example strip and case-insensitive comparison).
3. **For each song:** Build its 5D vector, compute **cosine similarity** between the user vector and the song vector to get a numeric match, set **genre_match** and **mood_match** to 1 when labels match the profile and 0 otherwise, then combine into a **weighted score** (numeric match plus bonuses; optional artist bonus if you implement it).
4. **Output:** Sort by score, apply **tie-breaks** (for example higher cosine, then genre match, then id), return the **top K** recommendations.

### User inputs required

The user supplies a **single dictionary** (or the same fields through a form or CLI). **Required:** `energy`, `valence`, `danceability`, and `acousticness` as decimals (roughly 0 to 1); **`tempo_bpm`** as beats per minute; **`genre`** and **`mood`** as **one string each**. **Optional:** `top_k` (how many results; default if omitted), and **`artist`** if you add a same-artist bonus. The system does not ask for catalog song IDs; taste is whatever numbers and labels the user enters.

### Biases and blind spots

- **Catalog bias:** Only songs in `songs.csv` can appear. Genres, moods, artists, and numeric ranges reflect whoever built that file, not the whole world of music.
- **Label bias:** Genre and mood are coarse strings. An exact match rule ignores near neighbors (for example “indie pop” vs “pop”) and favors whatever wording appears in the data.
- **Feature bias:** Five numbers plus two tags are a cartoon of real listening. They can track vibe roughly but miss lyrics, culture, era, social context, and intent that real users care about.
- **Weighting bias:** The relative weights on cosine vs genre vs mood encode a value judgment (for example “vibe first, labels second”). Different weights would reorder results with no single objectively correct choice.
- **User input bias:** Self-entered sliders and BPM can be inconsistent or unlike any real track; the system still scores faithfully against that input, which may not match how the user actually listens.
- **No diversity rule:** Top K by score can return a cluster of very similar rows unless you add extra rules later.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Bias

Experiments with saved runs (for example chill lofi, deep intense rock, the “pop” vs indie-pop profile, and classical/serene labels paired with club-like numeric sliders) surfaced one clear weakness: **the hybrid score treats genre and mood as all-or-nothing string equality with sizable bonuses**, while numeric similarity is a blended cosine over five features. That design **pushes users toward whatever wording appears in the catalog**—near neighbors such as “indie pop” vs “pop” or “relaxed” vs “chill” get **no partial credit**, so cross-genre but similar-vibe tracks can sink even when their features line up well. When labels and numbers disagree, **the label side can still win**: a matching classical/serene row outranked high-energy dance songs for the contradictory profile, so self-reported tags can **dominate felt vibe** under the current weights. **Energy is not modeled as its own gap** (it is just one cosine dimension among tempo, valence, danceability, and acousticness), so “how intense” never gets extra emphasis beyond that shared vector. Together, behavior resembles a **taxonomy-weighted filter bubble** more than a continuous similarity space across musical taste.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

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

