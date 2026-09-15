# Basic Turing Machine Simulator

A deterministic Turing Machine: an infinite two-way tape, a head, a current
state, and a transition function `(state, symbol) -> (new_state, write_symbol, direction)`.

Requires Python 3.9+ (uses builtin generic types like `tuple[...]`).

## Usage

```python
from turing_machine import binary_increment_machine

tm = binary_increment_machine()
result = tm.run("1011")
print(result.tape)      # "1100"
print(result.accepted)  # True
print(result.steps)     # 8
```

Run the built-in demo:

```
python turing_machine.py
```

## Included machines

- `binary_increment_machine()` — adds 1 to a binary number on the tape,
  handling carry propagation (`"111"` -> `"1000"`).
- `binary_complement_machine()` — flips every bit (`"1010"` -> `"0101"`).

Both are plain dictionaries of transitions passed into the generic
`TuringMachine` class — define your own transition table to build other
machines on the same engine.

## Tests

```
python -m unittest -v
```
