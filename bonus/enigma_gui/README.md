# Interactive Enigma GUI

A Flask web front-end for the [`enigma_simulator`](../../cryptanalysis/enigma_simulator)
engine: pick rotors, ring settings, start positions, a reflector, and
plugboard pairs, type a message, and see the ciphertext plus an
interactive Plotly chart of how each rotor's position advances letter by
letter (including the wraparound from position 25 back to 0).

Requires Python 3.12 — see the [repo root README](../../README.md#setup) for
venv setup.

## Setup

```
pip install -r requirements.txt
```

## Usage

```
python app.py
```

Then open <http://127.0.0.1:5000>. The dev server binds to localhost only
and runs with `debug=False` by default — this is a local demo tool, not
meant to be exposed or run in production.

Invalid input (duplicate rotors, a malformed plugboard pair, a missing
field) shows an inline error and preserves everything you'd already
entered, rather than crashing.

## Design notes

- Reuses `enigma_simulator`'s tested `EnigmaMachine`/`EnigmaSettings`
  directly via a `sys.path` addition (same "genuine engine reuse"
  exception as the cryptanalysis modules — see `CLAUDE.md`), rather than
  reimplementing the cipher.
- `EnigmaMachine` now rejects duplicate rotors (a real Enigma physically
  couldn't hold two of the same rotor) — a small correctness fix to the
  shared engine, made here because this is the first place a user could
  plausibly pick the same rotor twice by accident.

## Tests

```
python -m unittest -v
```

Tests cross-check the web form's output against calling `EnigmaMachine`
directly with equivalent settings, not just HTTP status codes, plus a
round-trip (encrypt, then decrypt via a second independent request) and
several invalid-input cases that should show an error rather than a 500.
