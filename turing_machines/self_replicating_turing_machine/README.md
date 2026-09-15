# Self-Replicating Turing Machine

Self-replication for a Turing Machine is usually explained through
Kleene's recursion theorem or von Neumann's universal constructor: a
machine can be built that, given a description of itself as data, can
produce a copy of that description as part of its own output — the same
split between "instructions" and "genome" that lets DNA be both
transcribed *and* copied.

This module builds that idea out of two pieces you can check independently:

1. **`TapeCopierTuringMachine`** — a real, general-purpose single-tape TM
   that copies any binary string `w` from a `w#` tape to `w#w`, using the
   classic mark-and-bounce construction: mark one symbol of `w` consumed,
   walk to the current end of the tape, append the remembered value,
   rewind, repeat.
2. **`self_replication_demo()`** — serializes the copier's *own*
   transition table into a bitstring (its "genome"), feeds that genome to
   the copier as the string to duplicate, and confirms the machine
   produces two bit-for-bit identical copies of its own description side
   by side on the tape. The copier's code is quite literally treated as
   data and copied by itself.

Requires Python 3.12 — see the [repo root README](../../README.md#setup) for
venv setup.

## Why the genome is a compact 5-character-per-rule encoding

Copying is the one operation in this repo that costs more than a handful
of steps: each of the `n` rounds re-scans up to the whole tape, so copying
a length-`n` string costs on the order of `n^2` steps. A naive,
human-readable serialization of the transition table (`state,symbol>...;`
text) runs to over a thousand characters — quadratic in that would be slow
even for a demo. `serialize_transitions()` instead assigns each state name
a single letter and encodes every rule as a fixed 5-character record
(`state, symbol, new_state, write_symbol, direction`), since tape symbols
are already single characters. That shrinks the genome from ~8,800 bits to
1,280 bits, and the whole self-replication run completes in under two
seconds and about 5 million steps.

## Usage

```python
from self_replicating_turing_machine import (
    TapeCopierTuringMachine, build_copy_tape, self_replication_demo,
)

tm = TapeCopierTuringMachine()
result = tm.run(build_copy_tape("101"))
print(result.tape)  # "101#101"

report = self_replication_demo()
print(report.genome_bits)                  # 1280
print(report.offspring_matches_original)    # True -- an exact copy of its own code
print(report.decoded_matches_source)        # True -- and it decodes back to the source
```

Run the built-in demo:

```
python self_replicating_turing_machine.py
```

## Tests

```
python -m unittest -v
```

Covers the generic copier against every binary string up to length 6
(checked exactly against the expected `w#w`), input validation, the
`text_to_bits`/`bits_to_text` round trip, serialization determinism, and
the central claim: that the copier, run on its own encoded transition
table, produces an output whose two halves are identical to each other
and to the original — and that decoding the copy back to text reproduces
the exact source description it started from.
