# Genetic Algorithm for Code Breaking

A genetic algorithm that cracks monoalphabetic substitution ciphers by
evolving a population of candidate 26-letter substitution keys (as
permutations) via tournament selection, order-preserving crossover, and
swap mutation.

Requires Python 3.12 — see the [repo root README](../../README.md#setup) for
venv setup.

## Why not just reuse `frequency_analysis`?

[`cryptanalysis/frequency_analysis`](../../cryptanalysis/frequency_analysis)
already has `frequency_substitution_guess`: a single, deterministic guess
that ranks ciphertext letters by frequency and matches them against the
reference English letter-frequency ranking. It's fast, but only reliable
when the ciphertext's letter frequencies already closely track that
reference distribution — short or unusual texts throw it off, and it has
no way to recover from a wrong guess.

This module instead searches the full permutation space (26!, far too
large to brute force) using a fitness function that rewards recognizable
English words appearing in the decryption — word boundaries survive
substitution encryption unchanged, since only letters get substituted —
with letter-frequency chi-squared (reusing `frequency_analysis`'s tested
`chi_squared_statistic`) as a secondary signal that still gives useful
gradient before any whole words decrypt correctly. That combination lets
it recover the correct key even from ciphertext whose frequencies don't
line up neatly with the English reference table.

## Usage

```python
from genetic_codebreaker import crack_substitution_cipher

result = crack_substitution_cipher(ciphertext)
print(result.plaintext, result.fitness, result.generations_run)
```

Run the built-in demo (a simple Atbash-style substitution cipher):

```
python genetic_codebreaker.py
```

## Tests

```
python -m unittest -v
```

Covers the genetic operators in isolation (mutation swaps exactly two
positions, order crossover always yields a valid permutation and
preserves the copied parent slice), input validation, and an end-to-end
crack that recovers an exact known plaintext from a substitution cipher.
