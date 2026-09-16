# Automated Enigma Key Discovery

Given a known plaintext-ciphertext message pair (historically, often a
predictable message like a weather report or routine sign-off, confirmed
after the fact), automatically recovers the *full* Enigma key: rotor
order, start position, and plugboard wiring.

This isn't a machine-learning approach — it applies
[`bombe_simulator`](../bombe_simulator)'s menu-consistency technique
twice: first cheaply, against a short crib prefix, to find the correct
rotor order and start position out of the whole search space; then once
more, against the *entire* known plaintext, to resolve as much of the
plugboard as that much data supports (usually all of it, given enough
text). The result is verified by an exact decrypt-and-compare against the
full known plaintext, so a "discovered" key is never just a plausible
guess — `fully_verified` tells you whether it actually decrypts
correctly.

Ring settings are assumed known, matching
[`brute_force_cracker`](../brute_force_cracker) and `bombe_simulator`'s
scope.

Requires Python 3.12 — see the [repo root README](../../README.md#setup) for
venv setup.

## Usage

```python
from automated_key_discovery import discover_key

result = discover_key(known_plaintext, known_ciphertext)
print(result.rotor_names, result.start_positions, result.plugboard_pairs)
print(result.fully_verified)  # True if the decrypt-and-compare check passed
```

`crib_length` (default 16) controls how much of the plaintext prefix is
used for the first (rotor/position search) stage — longer gives better
pruning but costs more; the second stage always uses the full known
plaintext, so a longer message resolves more of the plugboard. Pass
`start_position_candidates` to restrict the search space (see
`bombe_simulator`'s README for why that matters for runtime).

Run the built-in demo (samples the position space for a fast run):

```
python automated_key_discovery.py
```

The demo recovers the exact rotor order, start position, and **all four**
plugboard pairs from a ~68-letter known message, with `fully_verified=True`.

## Tests

```
python -m unittest -v
```
