"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    # -------------------------------------------------------------------------
    # User profiles: keep exactly ONE active `user_prefs = {...}` assignment.
    # Comment out the current block and uncomment another to run it.
    # Keys match recommender / plan.md (genre, mood, numerics 0–1, tempo_bpm).
    # -------------------------------------------------------------------------

    # --- "High-Energy Pop" — bright, danceable, radio-pop shaped ---
    # user_prefs = {
    #     "genre": "pop",
    #     "mood": "happy",
    #     "energy": 0.88,
    #     "tempo_bpm": 128,
    #     "valence": 0.86,
    #     "danceability": 0.84,
    #     "acousticness": 0.14,
    # }

    # --- "Chill Lofi" — soft, slow, acoustic-leaning (matches lofi rows well) ---
    # user_prefs = {
    #     "genre": "lofi",
    #     "mood": "chill",
    #     "energy": 0.36,
    #     "tempo_bpm": 75,
    #     "valence": 0.58,
    #     "danceability": 0.61,
    #     "acousticness": 0.82,
    # }

    # --- "Deep Intense Rock" — heavy, driving, lower valence ---
    # user_prefs = {
    #     "genre": "rock",
    #     "mood": "intense",
    #     "energy": 0.92,
    #     "tempo_bpm": 150,
    #     "valence": 0.44,
    #     "danceability": 0.64,
    #     "acousticness": 0.11,
    # }

    # ========== Adversarial / edge-case profiles ==========
    # These probe hybrid scoring: exact genre/mood bonuses vs cosine, clamping,
    # defaults for missing keys, and label quirks (e.g. "pop" vs "indie pop").

    # "Subgenre label trap" — says "pop" (exact match only). "Indie pop" songs
    # get NO genre bonus but can still win on numeric vibe; compare to true pop.
    # user_prefs = {
    #     "genre": "pop",
    #     "mood": "happy",
    #     "energy": 0.78,
    #     "tempo_bpm": 122,
    #     "valence": 0.82,
    #     "danceability": 0.80,
    #     "acousticness": 0.30,
    # }

    # "Contradictory genre vs vibe" — classical + serene labels but EDM-like
    # numerics; checks whether cosine pulls toward house/hip-hop despite labels.
    user_prefs = {
        "genre": "classical",
        "mood": "serene",
        "energy": 0.94,
        "tempo_bpm": 128,
        "valence": 0.88,
        "danceability": 0.90,
        "acousticness": 0.08,
    }


    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
