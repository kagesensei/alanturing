# Enigma Machine Simulator

A digital recreation of the Wehrmacht/Luftwaffe Enigma I: three rotors
(chosen from historical rotors I-V), a reflector (A/B/C), and a plugboard.
Uses the historical rotor and reflector wirings, and reproduces the
well-known rotor "double-stepping" anomaly.

Requires Python 3.12 — see the [repo root README](../../README.md#setup) for
venv setup.

## Usage

```python
from enigma import EnigmaMachine, EnigmaSettings

settings = EnigmaSettings(
    rotor_names=("I", "II", "III"),
    ring_settings=("A", "A", "A"),
    start_positions=("A", "A", "A"),
    reflector_name="B",
    plugboard_pairs=(("A", "B"), ("C", "D")),
)

machine = EnigmaMachine(settings)
ciphertext = machine.encrypt_message("ENIGMAWASBROKENBYTURING")

# Enigma is symmetric: the same settings on a fresh machine decrypt it.
decoder = EnigmaMachine(settings)
plaintext = decoder.encrypt_message(ciphertext)
```

Run the built-in demo:

```
python enigma.py
```

## Correctness

`test_known_reference_vector` checks the implementation against a widely
published Enigma I reference test vector: rotors I, II, III, reflector B,
all ring settings and start positions at `A`, no plugboard — encrypting
`"AAAAA"` produces `"BDZGO"`.

## Tests

```
python -m unittest -v
```
