# Music recommender simulation — finalized plan

This document records the **content-based** design for the startup music platform simulation: modular Python, **no ML libraries**, mostly vanilla Python (lists, dicts, `math`, CSV).

---

## Data source

- **`data/songs.csv`** columns used for recommendations:
  - **Numeric:** `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`
  - **Categorical:** `genre`, `mood`
  - **Metadata (not in similarity vector):** `id`, `title`, `artist` — `artist` optional for a small tie-break bonus; `title` not used for scoring

---

## User profile: inputs and derived data

The user does **not** pick catalog song IDs. They supply a **single dictionary** (or equivalent object) with numeric fields and **one string each** for genre and mood.

### Example profile input

```python
{
    "energy": 0.7,
    "tempo_bpm": 120,
    "valence": 0.8,
    "danceability": 0.75,
    "acousticness": 0.2,
    "genre": "pop",
    "mood": "happy",
}
```

- **`energy`, `valence`, `danceability`, `acousticness`:** decimals in roughly the **0–1** range (same meaning as in the CSV).
- **`tempo_bpm`:** a **BPM** the user understands; the system converts it with the **same catalog-wide min–max scaling** used for songs so the second component of the 5D vector stays comparable.
- **`genre`, `mood`:** each a **single string** (no lists). Compare to songs after **normalization** (e.g. strip whitespace, case-insensitive match) so `"Pop"` and `"pop"` count as the same.

### Optional keys

- **`top_k`:** how many recommendations to return (default `5` if omitted).
- **`artist`:** optional single string if you implement an **artist bonus**; otherwise omit.

### What the system builds from that dict

| Field | Role |
|-------|------|
| **User 5D vector** | `[energy, tempo_scaled, valence, danceability, acousticness]` using catalog `bpm_min` / `bpm_max` for `tempo_scaled`. |
| **Target `genre` / `mood` strings** | Stored (normalized) for categorical bonuses only. |

### Finalized match rules (categorical)

- **`genre_match`:** `1` if the candidate song’s `genre` (normalized) equals the profile’s `genre` (normalized), else `0`.
- **`mood_match`:** `1` if the candidate song’s `mood` (normalized) equals the profile’s `mood` (normalized), else `0`.

### Edge cases and validation

- **Out-of-range decimals:** clamp to `[0, 1]` for the four non-tempo numerics, or reject; document the choice.
- **Unknown genre/mood:** string still works for matching; if no song uses that label, bonuses are simply `0` for every candidate (cosine still ranks).
- **Demos / tests:** pass a literal dict (like the example above) for reproducible runs.

---

## Features — what matters and why


| Feature                                             | Use                                                                                           |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `energy`, `valence`, `danceability`, `acousticness` | Direct numeric “vibe” dimensions (already ~0–1)                                               |
| `tempo_bpm`                                         | Same vector, but **must be scaled** so it does not dominate cosine similarity vs 0–1 features |
| `genre`                                             | Strong user preference signal — match bonus (or filter-then-rank)                             |
| `mood`                                              | Intent / context (chill vs intense) — match bonus                                             |
| `artist`                                            | Optional small boost or tie-break only (identity, not general taste)                          |


---

## Song vector (for cosine similarity)

Each **candidate song** (and the **user profile**) uses one **5-dimensional** numeric vector, **fixed component order**:

1. `energy`
2. `tempo_scaled` — BPM after catalog-wide scaling (see below)
3. `valence`
4. `danceability`
5. `acousticness`

**Not included as raw strings in this vector:** `genre`, `mood` (handled separately in the hybrid score).

### Tempo scaling (compute once on the full catalog)

- **Min–max:** `tempo_scaled = (bpm - bpm_min) / (bpm_max - bpm_min)` → second dimension in [0, 1] like the others

Use the **same** `bpm_min` / `bpm_max` (or mean / std) for every song and for the user profile.

### User profile vector

- The **user vector** `u` is built from the profile dict: same **5D order** as songs, with **`tempo_bpm`** scaled using the catalog’s `bpm_min` / `bpm_max` (see [User profile: inputs and derived data](#user-profile-inputs-and-derived-data)).
- Cosine similarity is computed between **user vector** and each **candidate song vector**.

### Cosine similarity

- Standard formula: \(\cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{s}}{\|\mathbf{u}\| \|\mathbf{s}\|}\)
- Values in [-1, 1]; for ranking, higher is better. Optionally map or clip to [0, 1] for a `sim_num` term if you want it bounded for weighting.

---

## Final score (hybrid: numeric + categorical)

Combine **cosine-based numeric match** with **simple categorical rules** (no embeddings):


\text{score} = w_n \cdot \text{simnum} + w_g \cdot \text{genrematch} + w_m \cdot \text{moodmatch}


- **`sim_num`:** derived from cosine similarity between user 5D vector and song 5D vector (e.g. cosine itself, or rescaled to [0,1]).
- **`genre_match`:** `1` if song `genre` matches the profile’s `genre` string (normalized), else `0` (see [User profile](#user-profile-inputs-and-derived-data)).
- **`mood_match`:** `1` if song `mood` matches the profile’s `mood` string (normalized), else `0`.

**Starting weights (tunable):** `w_n = 0.6`, `w_g = 0.25`, `w_m = 0.15` — vibe dominates; genre/mood break ties and keep results interpretable.

**Optional:** `+ w_a * artist_match` (e.g. `w_a = 0.05`) if the profile includes a preferred `artist` string and the candidate’s `artist` matches (normalized).

**Tie-breaking (suggested):** higher `sim_num`, then higher `genre_match`, then `id`.

---

## Data flow

End-to-end path from preferences to ranked suggestions.

### One-line spine

**Input (profile dict + CSV)** → **setup:** user 5D vector + catalog tempo bounds → **loop:** each song gets a vector, cosine + label matches, weighted **score** → **sort** → **top K** → **output** (ordered list, optional explanations).

### 1. Input (user prefs + catalog)

- **Profile dict:** `energy`, `valence`, `danceability`, `acousticness`, `tempo_bpm`, `genre`, `mood`; optional `top_k`, `artist`.
- **Catalog:** load `songs.csv` (all rows are candidates unless you add filters later).

### 2. Setup (once per run, before the loop)

- Parse songs into structures you can score.
- Compute **BPM min / max** (or chosen tempo scaling stats) across the catalog.
- From the profile dict, build the **user 5D vector** (same component order as songs; scale the user’s BPM with the same formula as songs).
- **Normalize** profile `genre` and `mood` strings for comparisons.
- Optionally **clamp** the four 0–1 inputs per [Edge cases and validation](#edge-cases-and-validation).

### 3. Process (the loop: judge every song)

For **each** catalog row:

- Build that song’s **5D vector** (same tempo scaling).
- **`sim_num`:** cosine similarity between **user vector** and **song vector** (optionally rescaled for weighting).
- **`genre_match` / `mood_match`:** `1` or `0` using normalized string equality vs the song’s `genre` / `mood`.
- **`score`:** weighted mix from **Final score** (`w_n`, `w_g`, `w_m`, plus optional artist term).
- Record **score** with **song id** (and tie-break keys if needed).

### 4. Output (ranking: top K)

- **Sort** all scored candidates by `score`, then apply **tie-breaking** (e.g. higher `sim_num`, then `genre_match`, then `id`).
- Take the **top `k`** (`top_k` from profile, or default such as `5`).
- **Return** ordered recommendations (e.g. id, title, artist) and optionally a short **why** (nearby features, genre/mood hit).

---

## Implementation constraints (finalized)

- **No ML models** — no `sklearn`, neural nets, or training loops.
- **Vanilla Python** — load CSV with `csv` or similar; similarity with loops and `math.sqrt`; optional `json` for configs.
- **Interpretable** — explain scores as “close in energy/valence/… plus genre/mood match.”

---

