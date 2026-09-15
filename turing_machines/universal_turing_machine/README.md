# Universal Turing Machine

Turing's 1936 insight was that a machine's description can itself be data.
Where the [basic simulator](../basic_simulator) takes a transition table as a
Python object, this `UniversalTuringMachine` takes it **encoded on the
tape**, alongside the input. One fixed `step` function then simulates
whatever machine the tape describes.

Requires Python 3.12 — see the [repo root README](../../README.md#setup) for
venv setup.

## Tape format

A single string holds the entire configuration:

```
<description>##<left>[<state>:<symbol>]<right>
```

- `description` — the encoded transition table, one rule per
  `state,symbol>new_state,write,dir;`.
- `##` — separates the description from the machine being simulated.
- `<left>` / `<right>` — tape contents on either side of the head.
- `[state:symbol]` — the head marker: current state and the symbol under the
  head, embedded directly in the tape text.

Each step re-scans the description for a rule matching the current
`state,symbol` pair, fresh every time — the same way a real universal
machine has no separate memory for the table it's interpreting, only the
tape.

## Usage

```python
from universal_turing_machine import (
    UniversalTuringMachine, binary_increment_transitions, encode_transitions, build_tape,
)

utm = UniversalTuringMachine(accept_states={"halt"})
description = encode_transitions(binary_increment_transitions())
tape = build_tape(description, "1011", initial_state="right")

result = utm.run(tape)
print(result.tape)      # "1100"
print(result.accepted)  # True
```

The same `utm` instance can simulate a completely different machine just by
handing it a different encoded description — that's the point of a UTM. See
`SameTapeDifferentMachineTests` in the test suite.

Run the built-in demo:

```
python universal_turing_machine.py
```

## Included machines

`binary_increment_transitions()` and `binary_complement_transitions()`
mirror the basic simulator's machines, expressed as plain data so they can be
encoded onto a tape. Build your own transition table and pass it through
`encode_transitions()` / `build_tape()` to simulate anything else.

## Tests

```
python -m unittest -v
```
