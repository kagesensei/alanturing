# Simulated Bombe Machine

A simplified simulation of Turing's Bombe. Its key insight, reproduced
here: the Enigma plugboard never has to be brute forced. For a candidate
rotor order and start position, a "menu" built from a crib (a known
plaintext fragment aligned with ciphertext) can be checked for
*consistency* — do the crib's repeated letters force a contradiction? —
without ever guessing a plugboard wiring. A rotor order/position with no
contradiction is a "stop": a candidate worth testing further, with the
plugboard wiring the crib's menu deduced along the way.

Ring settings are assumed known, matching
[`brute_force_cracker`](../brute_force_cracker)'s scope. Builds on
[`enigma_simulator`](../enigma_simulator) — see the note at the top of
`bombe.py`.

Requires Python 3.12 — see the [repo root README](../../README.md#setup) for
venv setup.

## Usage

```python
from bombe import find_bombe_stops

stops = find_bombe_stops(ciphertext, crib="ATTACKATDAWN")
for stop in stops:
    print(stop.rotor_names, stop.start_positions, stop.plugboard)
```

`find_bombe_stops` searches all 17,576 start positions by default; pass a
smaller `start_position_candidates` list to restrict the search (e.g. to
positions already narrowed down some other way, or for a fast demo run).

Run the built-in demo (samples the position space for a fast run — a few
seconds instead of ~90):

```
python bombe.py
```

## How much pruning it actually gets

A crib's usefulness depends entirely on its connectivity — repeated
letters that let the consistency check chain across multiple positions
(what Bletchley Park called "loops" in a menu). A short or non-repeating
crib resolves almost nothing: testing shows `"ATTACK"` (6 letters)
produces *no* pruning at all against a 3-rotor pool. The full
`"ATTACKATDAWN"` (12 letters, with `A` and `T` each repeating) prunes
6 rotor orders × 17,576 positions (105,456 candidates) down to just
10 stops — and the deduced plugboard for the true stop correctly recovers
every pairing the crib's menu actually touches.

The returned plugboard is only ever **partial**: it covers just the
letters connected to the crib's menu graph. That's historically accurate
— resolving the rest required either a richer crib or further hand work,
both out of scope here.

## Tests

```
python -m unittest -v
```

Tests restrict the position search (via `start_position_candidates`) to
keep the suite fast; the numbers above (from the full 105,456-candidate
search) are demonstrated by the demo script instead.
