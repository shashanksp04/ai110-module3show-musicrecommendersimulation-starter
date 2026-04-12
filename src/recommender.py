import csv
import math
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

# Hybrid weights (plan.md): numeric vibe dominates; genre/mood interpretable bonuses
W_NUM = 0.6
W_GENRE = 0.25
W_MOOD = 0.15
W_ARTIST = 0.05


def normalize_label(value: Any) -> str:
    """
    Normalize a categorical string for comparison (genre, mood, artist).

    Usage: pass raw CSV or user input values so that Pop and pop (after strip)
    compare equal. ``None`` becomes an empty string (no match).
    """
    if value is None:
        return ""
    return str(value).strip().lower()


def clamp01(x: float) -> float:
    """
    Clamp a numeric preference or feature to the inclusive range [0, 1].

    Usage: apply to energy, valence, danceability, and acousticness before
    building vectors or hybrid scores so out-of-range user input is safe.
    """
    return max(0.0, min(1.0, float(x)))


def catalog_bpm_range(songs: List[Dict]) -> Tuple[float, float]:
    """
    Compute catalog-wide minimum and maximum tempo (BPM) for scaling.

    Usage: call once per catalog (or recommender instance) and pass the
    returned ``(bpm_min, bpm_max)`` into ``tempo_scaled`` / ``vector_from_row``
    so user and song tempo dimensions are comparable. If the list is empty,
    returns a sensible default range; if all BPMs are equal, widens the range
    slightly to avoid division by zero.
    """
    if not songs:
        return 60.0, 180.0
    bpms = [float(s["tempo_bpm"]) for s in songs]
    lo, hi = min(bpms), max(bpms)
    if hi <= lo:
        lo, hi = lo - 1.0, hi + 1.0
    return lo, hi


def tempo_scaled(bpm: float, bpm_min: float, bpm_max: float) -> float:
    """
    Min-max scale a BPM value into [0, 1] using catalog bounds.

    Usage: pass the same ``bpm_min`` and ``bpm_max`` for every song and for
    the user's target BPM so the second dimension of the 5D feature vector
    does not dominate cosine similarity.
    """
    if bpm_max <= bpm_min:
        return 0.5
    return clamp01((float(bpm) - bpm_min) / (bpm_max - bpm_min))


def vector_from_row(
    energy: float,
    tempo_bpm: float,
    valence: float,
    danceability: float,
    acousticness: float,
    bpm_min: float,
    bpm_max: float,
) -> List[float]:
    """
    Build the 5D content vector: energy, scaled tempo, valence, danceability, acousticness.

    Usage: call with user preference fields or song dict fields plus the catalog
    ``bpm_min``/``bpm_max`` from ``catalog_bpm_range``. The order is fixed for
    cosine similarity with ``cosine_similarity``.
    """
    return [
        clamp01(energy),
        tempo_scaled(tempo_bpm, bpm_min, bpm_max),
        clamp01(valence),
        clamp01(danceability),
        clamp01(acousticness),
    ]


def cosine_similarity(u: List[float], v: List[float]) -> float:
    """
    Cosine similarity between two same-length numeric vectors.

    Usage: pass two vectors from ``vector_from_row`` (user vs song). Returns
    a value in [-1, 1]; higher means closer direction. Returns 0.0 if either
    vector has zero length to avoid division by zero.
    """
    dot = sum(a * b for a, b in zip(u, v))
    nu = math.sqrt(sum(a * a for a in u))
    nv = math.sqrt(sum(b * b for b in v))
    if nu == 0.0 or nv == 0.0:
        return 0.0
    return dot / (nu * nv)


def sim_num_from_cosine(cos: float) -> float:
    """
    Map cosine similarity from [-1, 1] to [0, 1] for the hybrid score.

    Usage: feed the output of ``cosine_similarity`` here before multiplying by
    ``W_NUM`` so the numeric term is on the same scale as genre/mood matches.
    """
    return (cos + 1.0) / 2.0


def default_prefs_for_partial_dict(
    user_prefs: Dict, bpm_min: float, bpm_max: float
) -> Dict[str, Any]:
    """
    Build a full preference dict when the caller omits some keys.

    Usage: pass a partial ``user_prefs`` (e.g. only genre/mood/energy) plus
    catalog BPM bounds. Missing numerics get defaults; missing ``tempo_bpm``
    defaults to the catalog midpoint. ``recommend_songs`` and ``score_song``
    merge this with explicit user keys next.
    """
    mid = (bpm_min + bpm_max) / 2.0
    return {
        "energy": clamp01(float(user_prefs.get("energy", 0.5))),
        "valence": clamp01(float(user_prefs.get("valence", 0.6))),
        "danceability": clamp01(float(user_prefs.get("danceability", 0.65))),
        "acousticness": clamp01(float(user_prefs.get("acousticness", 0.35))),
        "tempo_bpm": float(user_prefs.get("tempo_bpm", mid)),
        "genre": user_prefs.get("genre", ""),
        "mood": user_prefs.get("mood", ""),
        "artist": user_prefs.get("artist"),
    }


def score_components(
    user_prefs: Dict, song: Dict, bpm_min: float, bpm_max: float
) -> Dict[str, Any]:
    """
    Compute hybrid score parts for one user--song pair.

    Usage: ``user_prefs`` must already contain energy, tempo_bpm, valence,
    danceability, acousticness, genre, mood (and optional artist). Returns a
    dict with ``score``, ``sim_num``, match flags, raw ``cosine``, and
    ``reasons`` strings for explanations. Used internally by ``score_song``,
    ``recommend_songs``, and ``Recommender``.
    """
    g_user = normalize_label(user_prefs.get("genre"))
    m_user = normalize_label(user_prefs.get("mood"))
    artist_pref = user_prefs.get("artist")

    u = vector_from_row(
        float(user_prefs["energy"]),
        float(user_prefs["tempo_bpm"]),
        float(user_prefs["valence"]),
        float(user_prefs["danceability"]),
        float(user_prefs["acousticness"]),
        bpm_min,
        bpm_max,
    )
    svec = vector_from_row(
        float(song["energy"]),
        float(song["tempo_bpm"]),
        float(song["valence"]),
        float(song["danceability"]),
        float(song["acousticness"]),
        bpm_min,
        bpm_max,
    )

    cos = cosine_similarity(u, svec)
    sim_num = sim_num_from_cosine(cos)
    genre_match = 1 if g_user and g_user == normalize_label(song.get("genre")) else 0
    mood_match = 1 if m_user and m_user == normalize_label(song.get("mood")) else 0
    artist_match = 0
    if artist_pref is not None and str(artist_pref).strip():
        if normalize_label(artist_pref) == normalize_label(song.get("artist")):
            artist_match = 1

    score = (
        W_NUM * sim_num
        + W_GENRE * genre_match
        + W_MOOD * mood_match
        + W_ARTIST * artist_match
    )

    reasons: List[str] = []
    reasons.append(f"Numeric vibe match (cosine-based similarity): {sim_num:.2f} on a 0-1 scale.")
    if genre_match:
        reasons.append(f"Genre matches your preference ({song.get('genre', '')}).")
    else:
        reasons.append("Genre differs from your preference.")
    if mood_match:
        reasons.append(f"Mood matches your intent ({song.get('mood', '')}).")
    else:
        reasons.append("Mood differs from your preference.")
    if artist_match:
        reasons.append("Artist matches your stated favorite.")
    reasons.append(
        f"Features: energy {song['energy']:.2f}, valence {song['valence']:.2f}, "
        f"danceability {song['danceability']:.2f}, acousticness {song['acousticness']:.2f}."
    )

    return {
        "score": score,
        "sim_num": sim_num,
        "genre_match": genre_match,
        "mood_match": mood_match,
        "cosine": cos,
        "reasons": reasons,
    }


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences (aligned with plan.md profile dict).
    Required by tests/test_recommender.py
    """

    genre: str
    mood: str
    energy: float
    valence: float
    danceability: float
    acousticness: float
    tempo_bpm: float
    artist: Optional[str] = None


def user_profile_to_prefs(user: UserProfile) -> Dict[str, Any]:
    """
    Convert a ``UserProfile`` dataclass into the dict shape used for scoring.

    Usage: call before ``score_components`` inside ``Recommender.recommend`` or
    ``explain_recommendation`` so the OOP API shares the same logic as
    ``recommend_songs``. Clamps 0-1 fields; passes through ``tempo_bpm``.
    """
    return {
        "energy": clamp01(user.energy),
        "valence": clamp01(user.valence),
        "danceability": clamp01(user.danceability),
        "acousticness": clamp01(user.acousticness),
        "tempo_bpm": float(user.tempo_bpm),
        "genre": user.genre,
        "mood": user.mood,
        "artist": user.artist,
    }


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        """Store the catalog as ``Song`` objects for ranking and explanations."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """
        Return up to ``k`` songs ranked by hybrid score for the given user.

        Usage: construct ``Recommender`` with a list of ``Song`` values, then
        pass a ``UserProfile``. Tie-breaking: higher score, then higher numeric
        similarity, then genre match, then lower song id.
        """
        dlist = [asdict(s) for s in self.songs]
        bpm_min, bpm_max = catalog_bpm_range(dlist)
        prefs = user_profile_to_prefs(user)

        ranked: List[Tuple[Song, float, float, int]] = []
        for s in self.songs:
            sd = asdict(s)
            comp = score_components(prefs, sd, bpm_min, bpm_max)
            ranked.append(
                (s, comp["score"], comp["sim_num"], comp["genre_match"])
            )

        ranked.sort(
            key=lambda t: (-t[1], -t[2], -t[3], t[0].id),
        )
        return [t[0] for t in ranked[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """
        Produce a single human-readable explanation for why ``song`` fits ``user``.

        Usage: call after ``recommend`` (or for any catalog song) to show score
        and feature/match reasons using the same BPM range as the full catalog.
        """
        dlist = [asdict(s) for s in self.songs]
        bpm_min, bpm_max = catalog_bpm_range(dlist)
        prefs = user_profile_to_prefs(user)
        comp = score_components(prefs, asdict(song), bpm_min, bpm_max)
        parts = [f"Overall match score: {comp['score']:.2f}."]
        parts.extend(comp["reasons"])
        return " ".join(parts)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Load the music catalog from a CSV file into a list of song dicts.

    Usage: pass a path such as data/songs.csv (relative to the process working
    directory). Skips blank rows; coerces id and tempo to integers and
    audio features to floats so downstream math works. Prints load progress.
    """
    print(f"Loading songs from {csv_path}...")
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row or not row.get("id"):
                continue
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": int(float(row["tempo_bpm"])),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                }
            )

    print(f"Loaded {len(songs)} songs")

    return songs


def score_song(
    user_prefs: Dict,
    song: Dict,
    bpm_min: float = 60.0,
    bpm_max: float = 200.0,
) -> Tuple[float, List[str]]:
    """
    Score one catalog song against user preferences.

    Usage: ``user_prefs`` may be partial (defaults filled like in
    ``recommend_songs``). Pass ``bpm_min`` and ``bpm_max`` from
    ``catalog_bpm_range`` over the full catalog when comparing multiple songs;
    the defaults (60, 200) are only for standalone calls. Returns
    ``(total_score, reason_strings)``.
    """
    filled = default_prefs_for_partial_dict(user_prefs, bpm_min, bpm_max)
    # Overlay explicit keys from user_prefs (genre, mood, artist, numerics)
    for key in ("energy", "valence", "danceability", "acousticness", "tempo_bpm", "genre", "mood", "artist"):
        if key in user_prefs:
            filled[key] = user_prefs[key]
    filled["energy"] = clamp01(float(filled["energy"]))
    filled["valence"] = clamp01(float(filled["valence"]))
    filled["danceability"] = clamp01(float(filled["danceability"]))
    filled["acousticness"] = clamp01(float(filled["acousticness"]))
    filled["tempo_bpm"] = float(filled["tempo_bpm"])

    comp = score_components(filled, song, bpm_min, bpm_max)
    return comp["score"], comp["reasons"]


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """
    Rank the catalog and return the top ``k`` recommendations (functional API).

    Usage: pass a preference dict (``genre``, ``mood``, numeric fields; optional
    ``artist``, ``top_k`` overrides ``k``). Each result is
    ``(song_dict, score, explanation_string)``. Uses catalog BPM min/max for
    scaling. Returns an empty list if ``songs`` is empty.
    """
    if not songs:
        return []

    k = int(user_prefs.get("top_k", k))
    bpm_min, bpm_max = catalog_bpm_range(songs)
    base = default_prefs_for_partial_dict(user_prefs, bpm_min, bpm_max)
    for key in ("energy", "valence", "danceability", "acousticness", "tempo_bpm", "genre", "mood", "artist"):
        if key in user_prefs:
            base[key] = user_prefs[key]
    base["energy"] = clamp01(float(base["energy"]))
    base["valence"] = clamp01(float(base["valence"]))
    base["danceability"] = clamp01(float(base["danceability"]))
    base["acousticness"] = clamp01(float(base["acousticness"]))
    base["tempo_bpm"] = float(base["tempo_bpm"])

    ranked: List[Tuple[Dict, float, float, int, List[str]]] = []
    for song in songs:
        comp = score_components(base, song, bpm_min, bpm_max)
        ranked.append(
            (
                song,
                comp["score"],
                comp["sim_num"],
                comp["genre_match"],
                comp["reasons"],
            )
        )

    ranked.sort(
        key=lambda t: (-t[1], -t[2], -t[3], t[0]["id"]),
    )

    out: List[Tuple[Dict, float, str]] = []
    for song, score, _, _, reasons in ranked[:k]:
        explanation = " ".join(reasons)
        out.append((song, score, explanation))
    return out
