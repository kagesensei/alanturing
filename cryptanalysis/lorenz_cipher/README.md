# Lorenz Cipher Simulator & Cracker

A simulator for the Lorenz SZ40 teleprinter cipher (codenamed "Tunny" at
Bletchley Park) — the cipher used for high-level German strategic
communications, more complex than Enigma and broken without the Allies
ever seeing the machine itself, work that directly led to Colossus, the
first programmable electronic computer.

Historical facts modeled here (verified against Wikipedia's "Lorenz
cipher" article): 5 chi wheels (lengths 41, 31, 29, 26, 23) that step
every character; 5 psi wheels (lengths 43, 47, 51, 53, 59) that step only
when the machine's "limitation" allows; two motor wheels (Mu61, Mu37)
that gate that limitation; and an XOR (Vernam) combination of the
chi-stream and psi-stream with the plaintext, in the 5-bit ITA2
(Baudot-Murray) teleprinter code. **Simplifications**, documented so scope
is clear: only the SZ40's stepping rule is modeled (SZ42a's extra
"second chi wheel" limitation check is not); only ITA2's letters-shift
code is supported (figures-shift and control characters are out of
scope); and wheel *pin patterns* are supplied by the caller rather than
hard-coded, since — unlike Enigma's fixed rotor wiring — they were a
configurable daily key, not fixed hardware.

Requires Python 3.12 — see the [repo root README](../../README.md#setup) for
venv setup.

## Usage

```python
from lorenz import LorenzMachine, LorenzSettings

settings = LorenzSettings(
    chi_pins=(...),   # 5 strings of 0/1, lengths 41,31,29,26,23
    psi_pins=(...),   # 5 strings of 0/1, lengths 43,47,51,53,59
    mu61_pins=...,    # a 61-character string of 0/1
    mu37_pins=...,    # a 37-character string of 0/1
)

cipher_bits = LorenzMachine(settings).process_text("HELLO WORLD")
plaintext = LorenzMachine(settings).process_bits(cipher_bits)  # symmetric
```

Run the built-in demos:

```
python lorenz.py            # encrypt/decrypt round-trip
python lorenz_cracker.py    # known-plaintext chi-pattern recovery
```

## The cracker's scope

`lorenz_cracker.recover_chi_patterns` is a **known-plaintext attack**:
given a plaintext-ciphertext pair, the psi wheels' pin patterns, the
motor wheels' pin patterns, and every wheel's start position (all
assumed already known), it recovers the 5 chi wheels' pin patterns
exactly — deterministically, not statistically.

This models the second half of Bletchley Park's real two-stage process:
they first found each message's wheel *start positions* through
statistical search (the famous "1+2 break-in" and later, mechanized,
Colossus), then derived or confirmed the longer-lived wheel *patterns*
from enough depth of known traffic. This module models that second stage
only — with an exact known-plaintext pair rather than statistical
inference from ciphertext depth, since it's a much stronger starting
point and avoids a statistical test that would be fragile against a
handmade sample text with no guarantee of matching real German traffic's
statistics.

## Tests

```
python -m unittest -v
```
