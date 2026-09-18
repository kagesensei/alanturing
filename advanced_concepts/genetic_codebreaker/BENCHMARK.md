# Held-out substitution benchmark

Run `python benchmark.py` from this folder (Python 3.12, standard library).
The checked-in `benchmark_results.json` contains every prediction, seed,
parameter, timing, Python version, and operating system from the reference run.

Three original synthetic passages were authored after the existing solver and
fitness dictionary. They were not added to that dictionary. Two random
substitution keys (seeds 17 and 29) encrypt each passage; the genetic algorithm
runs with search seeds 0, 1, and 2 on each ciphertext. This gives six independent
ciphertexts, six deterministic frequency-baseline runs, and 18 genetic runs.
Each passage has equal weight in both method averages. These are held-out
evaluation fixtures, not a training corpus or a representative language sample.

Default genetic settings: population 200, 300 generations, mutation rate 0.15,
10 elites, tournament size 5. The solver and its dictionary were not tuned
after seeing these results. The third passage deliberately removes word
boundaries to expose the word-based fitness function's limitation.

| Method | Mean letter accuracy | Min–max | Exact recoveries | Mean time |
| --- | ---: | ---: | ---: | ---: |
| Frequency ranking | 22.2% | 17.0–35.6% | 0/6 | 0.000085 s |
| Genetic search | 14.8% | 0.0–48.2% | 0/18 | 5.14 s |

Accuracy counts ASCII letters only, excluding spaces and punctuation that both
methods preserve automatically. Exact recovery requires the entire plaintext
to match. Timings vary by hardware and load; tiny baseline durations are noisy.
Full-key recovery is not claimed: letters absent from a ciphertext cannot have
their mappings uniquely determined by that ciphertext.

The genetic search **underperforms frequency ranking on this small corpus**.
Its successful demo establishes a working search implementation, not general
cryptanalytic reliability. The dictionary is small and topic-heavy; short
unfamiliar vocabulary and missing word boundaries make its objective weak.
Future improvements should use a separately sourced language model (for
example character n-grams), a development corpus, and a new untouched test set.
Do not add these benchmark passages to the dictionary and call that progress.

The unit tests check scoring and reproducibility, not a minimum performance
threshold. Run this benchmark explicitly when evaluating solver changes;
the expensive search is not repeated during every CI run.
