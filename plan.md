# Music recommender simulation — finalized plan

This document records the **content-based** design for the startup music platform simulation: modular Python, **no ML libraries**, mostly vanilla Python (lists, dicts, `math`, CSV).

---

## Data source

- **`data/songs.csv`** columns used for recommendations:
  - **Numeric:** `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`
  - **Categorical:** `genre`, `mood`
  - **Metadata (not in similarity vector):** `id`, `title`, `artist` — `artist` optional for a small tie-break bonus; `title` not used for scoring

---

## Features — what matters and why

| Feature | Use |
|--------|-----|
| `energy`, `valence`, `danceability`, `acousticness` | Direct numeric “vibe” dimensions (already ~0–1) |
| `tempo_bpm` | Same vector, but **must be scaled** so it does not dominate cosine similarity vs 0–1 features |
| `genre` | Strong user preference signal — match bonus (or filter-then-rank) |
| `mood` | Intent / context (chill vs intense) — match bonus |
| `artist` | Optional small boost or tie-break only (identity, not general taste) |

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

- **Min–max:** `tempo_scaled = (bpm - bpm_min) / (bpm_max - bpm_min)` → second dimension in \([0, 1]\) like the others  

Use the **same** `bpm_min` / `bpm_max` (or mean / std) for every song and for the user profile.

### User profile vector

- Built in the **same 5D space**: e.g. **element-wise mean** of the 5D vectors of songs the user liked (or a fixed demo profile).
- Cosine similarity is computed between **user vector** and each **candidate song vector**.

### Cosine similarity

- Standard formula: \(\cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{s}}{\|\mathbf{u}\| \|\mathbf{s}\|}\)  
- Values in \([-1, 1]\); for ranking, higher is better. Optionally map or clip to \([0, 1]\) for a `sim_num` term if you want it bounded for weighting.

---

## Final score (hybrid: numeric + categorical)

Combine **cosine-based numeric match** with **simple categorical rules** (no embeddings):

\[
\text{score} = w_n \cdot \text{sim\_num} + w_g \cdot \text{genre\_match} + w_m \cdot \text{mood\_match}
\]

- **`sim_num`:** derived from cosine similarity between user 5D vector and song 5D vector (e.g. cosine itself, or rescaled to \([0,1]\)).
- **`genre_match`:** `1` if song genre matches user’s top / liked genre (or your rule), else `0`.
- **`mood_match`:** same for `mood`.

**Starting weights (tunable):** `w_n = 0.6`, `w_g = 0.25`, `w_m = 0.15` — vibe dominates; genre/mood break ties and keep results interpretable.

**Optional:** `+ w_a * artist_match` (e.g. `w_a = 0.05`) if same artist as a liked song.

**Tie-breaking (suggested):** higher `sim_num`, then higher `genre_match`, then `id`.

---

## Implementation constraints (finalized)

- **No ML models** — no `sklearn`, neural nets, or training loops.
- **Vanilla Python** — load CSV with `csv` or similar; similarity with loops and `math.sqrt`; optional `json` for configs.
- **Interpretable** — explain scores as “close in energy/valence/… plus genre/mood match.”

---

## Optional simplification

If you want a minimal v1: **cosine only** on the 5D vectors (`score = sim_num`), and add genre/mood bonuses in v2. Alternatively: **filter** to liked genres first, then rank by cosine only — very easy to explain in a demo.
