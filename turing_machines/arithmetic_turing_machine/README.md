# Turing Machine for Arithmetic

Two Turing Machines that compute over **unary** numbers, where the value
`k` is written as `k` copies of `"1"` (zero is the empty string). Unary is
the natural numeral system for a Turing Machine: "add one" and "remove
one" are single-cell edits, so the machines that do arithmetic on them
stay small enough to read by hand — unlike binary arithmetic, which needs
carry propagation.

Requires Python 3.12 — see the [repo root README](../../README.md#setup) for
venv setup.

## Usage

```python
from arithmetic_turing_machine import (
    addition_tape, subtraction_tape, unary_addition_machine, unary_subtraction_machine,
)

adder = unary_addition_machine()
result = adder.run(addition_tape(3, 2))
print(result.value)   # 5  (3 + 2)
print(result.tape)     # "11111"

subtractor = unary_subtraction_machine()
result = subtractor.run(subtraction_tape(2, 5))
print(result.value)   # 0  (monus: 2 - 5 clamps to 0, it never goes negative)
```

Run the built-in demo:

```
python arithmetic_turing_machine.py
```

## Included machines

- `unary_addition_machine()` reads a tape of the form `1^m + 1^n` (an
  `m`-run of ones, a `+` separator, an `n`-run of ones). It turns the `+`
  into a `1`, making one contiguous run of `m + n + 1` ones, then erases
  the last one -- leaving exactly `m + n`.

- `unary_subtraction_machine()` reads a tape of the form `1^m - 1^n` and
  computes the **monus** `max(m - n, 0)` (proper subtraction never goes
  negative). It repeatedly crosses off one not-yet-used digit from each
  side of the `-`. If the *right* side runs out first, whatever `1`s are
  still unconsumed on the left are exactly `m - n`. If the *left* side
  runs out first, `m <= n`, so the answer is 0 and the whole tape is
  swept blank.

`unary()`, `addition_tape()`, and `subtraction_tape()` are small helpers
for building well-formed input tapes and are validated against negative
counts.

## Tests

```
python -m unittest -v
```

Covers tape encoding, individual worked cases (including zero operands
and a genuinely negative-would-be subtraction result), and an exhaustive
0-5 by 0-5 grid for both operations, each result checked against Python's
own integer arithmetic.
