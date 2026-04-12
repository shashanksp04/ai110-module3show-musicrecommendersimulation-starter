# Profile comparison notes

Short comparisons between pairs of user profiles from `src/main.py`. Top‑5 outputs are from runs captured in `outputs/` where noted, and from a direct `recommend_songs` run for **High‑Energy Pop** (same scorer as `src.main`).

---

## High‑Energy Pop × Chill Lofi

**High‑Energy Pop** fills the top with bright **pop / happy** tracks (for example *Sunrise City*, *I Ain't Worried*) and high‑danceability picks such as *Gym Hero* and *Pulse District*; **Chill Lofi** instead promotes **lofi + chill** rows (*Library Rain*, *Midnight Coding*) and keeps softer, more acoustic neighbors below unless mood or genre bonuses apply. The swap is almost entirely explained by **opposite energy, tempo, and acousticness targets** in the cosine vector plus **different genre/mood bonuses**, so the outputs are valid stress tests for “party pop” versus “quiet study” taste.

---

## High‑Energy Pop × Deep Intense Rock

**Deep Intense Rock** puts *Storm Runner* (rock, intense, high energy, moderate valence) first, while **High‑Energy Pop** still prioritizes **pop + happy** perfect matches. Both lists reward **high energy and danceability**, so *Gym Hero* (intense pop) stays near the top in both runs as a **numeric bridge**; the main change is whether **rock/intense labels** or **pop/happy labels** earn the full hybrid bonus. That matches what the preferences are testing: **genre/mood gates** more than raw BPM alone.

---

## High‑Energy Pop × Subgenre label trap

These profiles share **pop** and **happy**, so the top three stay the same true‑pop rows; the trap profile’s slightly softer numbers change only **fine ordering** (for example *Gym Hero*’s score ticks down a hair) and the **fifth slot** (High‑Energy Pop favors *Pulse District*’s club‑like vector over *Velvet Hours*, which is farther on danceability/energy). The comparison checks that **small numeric shifts** still keep **label‑eligible** catalog rows on top—valid for “same aisle, different intensity.”

---

## High‑Energy Pop × Contradictory genre vs vibe

**High‑Energy Pop** yields a coherent **upbeat pop and dance** top five; **Contradictory genre vs vibe** names **classical / serene** but supplies **EDM‑like** numbers, and *Moonlight Sonata Redux* still wins with a **lower cosine** than *Pulse District* or *Gym Hero* because **both label bonuses** fire. The difference is the clearest sign that **declared genre and mood can beat the numeric vector** under current weights—surprising if you expect sliders to always “win,” but consistent with the hybrid formula.

---

## Chill Lofi × Deep Intense Rock

**Chill Lofi** tops **slow, acoustic‑leaning** lofi/chill tracks; **Deep Intense Rock** tops **fast, loud** rock/intense tracks with *Gym Hero* and punk/metal candidates further down driven by cosine without matching rock. Outputs are almost disjoint at rank one, which makes sense: the profiles target **opposite halves** of the energy–acousticness space and different **label pairs**.

---

## Chill Lofi × Subgenre label trap

**Chill Lofi** never surfaces **pop** in the top five because **pop/happy** bonuses never apply; **Subgenre label trap** never surfaces **lofi** for the same reason. Side‑by‑side, the lists show that **exact genre/mood strings** act like a **hard filter on the bonus terms**, even when another profile’s songs are still “pleasant” on pure numbers—useful for seeing **filter‑bubble** behavior between unrelated tags.

---

## Chill Lofi × Contradictory genre vs vibe

**Chill Lofi** ranks **lofi and ambient chill** highly; **Contradictory** elevates **classical serene** first, then a band of **perfect‑cosine dance/pop** tracks tied at **0.60** with **no** genre/mood match. Compared to Chill Lofi, the contradictory run shows **label‑matching classical** beating **numerically closer** party tracks, whereas Chill shows **matching lofi/chill** beating **only** numeric neighbors like jazz—same mechanism, different labels.

---

## Deep Intense Rock × Subgenre label trap

**Deep Intense Rock** favors **rock + intense** first, then other **intense** moods; **Subgenre label trap** favors **pop + happy** and never gives rock the genre bonus. *Gym Hero* appears in both lists as **high‑energy pop with intense mood**, illustrating how **shared mood or energy** can create overlap even when **genre preferences** diverge—outputs validate that mood and cosine can partially bridge genre.

---

## Deep Intense Rock × Contradictory genre vs vibe

**Deep Intense Rock** is built for **heavy, driving** tracks; **Contradictory** still ranks *Moonlight Sonata Redux* first despite **low energy** on the song because **classical/serene** matches the **user labels**. *Iron Foundry* (metal, aggressive) stays mid‑pack in the rock run **without** the intense mood tag, and in the contradictory run **every** non‑matching genre is capped around **numeric‑only** scores. The contrast highlights **synonym gaps** (intense vs aggressive) and **label‑first ranking** versus **headbanger‑style** numerics.

---

## Subgenre label trap × Contradictory genre vs vibe

**Subgenre label trap** keeps **true pop** rows above *Rooftop Lights* (**indie pop** gets **no** genre bonus but stays fourth on vibe and **happy** mood). **Contradictory** removes all pop bonuses and lets **classical** win first while **perfect numeric** matches to the user’s **club‑shaped** vector sit in a **flat 0.60 band**. The shift from trap to contradictory is mostly **which labels get +0.25/+0.15**, not a failure of cosine—it demonstrates that **profile validity** must be read as **hybrid** behavior, not “closest vector always on top.”
