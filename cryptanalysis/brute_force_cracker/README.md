# Brute Force Enigma Cracker

Given an Enigma ciphertext and a known plaintext fragment (a "crib"), tries
every rotor order and start position until it finds one whose decryption
begins with the crib. Ring settings and the plugboard are assumed already
known — brute-forcing those too isn't computationally feasible by exhaustive
search alone, which is exactly why the Bombe (a later roadmap item) exists.

Builds directly on [`enigma_simulator`](../enigma_simulator) rather than
reimplementing the Enigma machine — see the note at the top of
`brute_force_cracker.py` for how the import works.

Requires Python 3.12 — see the [repo root README](../../README.md#setup) for
venv setup.

## Usage

```python
from brute_force_cracker import crack

results = crack(ciphertext, crib="ATTACKAT")
for result in results:
    print(result.rotor_names, result.start_positions, result.decrypted)
```

By default the search covers all five historical rotors (I-V); pass a
smaller `available_rotors` tuple to narrow (and speed up) the search if you
know the pool was restricted, e.g. to the original three (`I`, `II`, `III`).

Run the built-in demo (searches the full 5-rotor pool — takes several
seconds):

```
python brute_force_cracker.py
```

## Tests

```
python -m unittest -v
```

Tests restrict the rotor pool to keep the suite fast; the full 5-rotor,
17,576-position search (1,053,600 combinations) is exercised by the demo
script instead.
