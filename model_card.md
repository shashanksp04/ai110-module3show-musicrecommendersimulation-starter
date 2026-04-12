# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

We checked behavior by running `python -m src.main` with the taste and stress-test profiles defined in `src/main.py`, saving representative console output under `outputs/` (`chill_lofi.txt`, `deep_intense_rock.txt`, `subgenre_label_trap.txt`, `contradic_genre_vibe.txt`) and comparing top‑5 lists side by side. The profiles we exercised were: **High‑Energy Pop** (bright pop/happy, high tempo and danceability); **Chill Lofi** (low energy, slow tempo, high acousticness, lofi/chill labels); **Deep Intense Rock** (high energy, faster tempo, lower valence, rock/intense labels); **Subgenre label trap** (still pop/happy but tuned so “indie pop” competes without an exact genre string match); and **Contradictory genre vs vibe** (classical/serene labels paired with club‑like numerics).

We looked for whether tops matched the **declared genre and mood** when both aligned with the catalog, whether **numeric vectors** pulled rankings toward the expected energy and acoustic “shape,” and whether **edge cases** exposed rigid rules (exact label match only, hybrid weights). What surprised us: **Chill Lofi** correctly flooded the top with lofi+chill rows, but **similarly soft jazz and ambient** tracks sat lower mostly because the **genre/mood bonuses never fired**, not because cosine hated them—so the list felt “right” for the label yet **narrow** for vibe. **Deep Intense Rock** put the only true **rock+intense** song first, but **metal** (high energy, low valence) ranked below **intense pop**, showing how **taxonomy wording** can outweigh a listener’s mental map of “heavy.” **Subgenre label trap** kept **Rooftop Lights** below true **pop** rows even with a strong happy/numeric fit—expected given exact genre equality, still stark in practice. Most striking was **Contradictory genre vs vibe**: **Moonlight Sonata Redux** won despite a **much weaker cosine** than house and pop hits, because **full genre and mood bonuses** outweighed the numeric profile—proof the hybrid can **override** the sliders when labels match. We did not rely on a separate accuracy metric; evaluation was **qualitative comparison across profiles** and the pairwise notes in `reflection.md`.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
