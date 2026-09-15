# Non-Deterministic Turing Machine (NTM) Simulator

A deterministic Turing Machine maps each `(state, symbol)` pair to exactly
one transition. A **non-deterministic** Turing Machine maps it to a *set*
of transitions, and conceptually takes all of them at once — the
computation forks into parallel branches. The machine accepts an input if
**any** branch reaches an accept state; it only rejects once **every**
branch has died out (no live branch remains) without ever accepting.

This simulator honors that semantics directly: `run()` performs a
breadth-first search across the whole frontier of live branches (rather
than first compiling the machine down to an equivalent deterministic one),
so the branching factor and search cost are visible in the result.

Requires Python 3.12 — see the [repo root README](../../README.md#setup) for
venv setup.

## Bounded by design

Because branches can multiply every step, `run()` takes two fixed, finite
resource ceilings:

- `max_steps` — the maximum search depth (BFS levels) to explore.
- `max_branches` — the maximum number of distinct configurations to ever
  visit, across all branches combined.

Both loops in `run()` are bounded solely by these constants, never by an
open-ended condition, so a call to `run()` always returns — even on a
machine that never halts on some branch. When a decision can't be reached
within those bounds, the result reports `halted=False` rather than
guessing.

## Usage

```python
from nondeterministic_turing_machine import contains_substring_machine

tm = contains_substring_machine("101")
result = tm.run("0110100")
print(result.accepted)          # True
print(result.accepting_tape)    # "0110100"
print(result.branches_explored) # how much parallel work was done
print(result.search_depth)      # how many BFS levels were explored
```

Run the built-in demo:

```
python nondeterministic_turing_machine.py
```

## Included machine

`contains_substring_machine(pattern)` builds an NTM over the alphabet
`{0, 1}` that accepts any string containing `pattern` as a substring. It is
the canonical "guess and verify" use of non-determinism: while scanning
left to right, the machine may *at any position* branch into a
verification path that commits to "the match starts here," while the
plain scanning branch keeps looking elsewhere in parallel. A branch that
guesses wrong simply has no further transition and quietly dies — it does
not cause rejection unless every branch dies.

Build your own `NTMTransitionTable` (a dict from `(state, symbol)` to a
`frozenset` of `(new_state, write_symbol, direction)` triples) and pass it
to `NondeterministicTuringMachine` to simulate a different machine.

## Tests

```
python -m unittest -v
```

Covers: acceptance/rejection correctness, overlapping and edge-position
matches, input validation, branch-count growth from non-determinism, and
that the search always terminates under both resource bounds even on
machines built to never halt.
