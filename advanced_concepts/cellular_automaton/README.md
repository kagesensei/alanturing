# Turing-Complete Cellular Automaton

An elementary (1D, 2-state, 3-neighbor) cellular automaton engine, per
Wolfram's standard 0-255 rule numbering, with a focus on **Rule 110** —
proven Turing-complete by Matthew Cook (2004), via a construction that
lets it simulate cyclic tag systems (themselves Turing-complete).

Requires Python 3.12 — see the [repo root README](../../README.md#setup) for
venv setup.

## Usage

```python
from cellular_automaton import run, render

result = run(rule_number=110, initial_state=[0]*39 + [1] + [0]*39, steps=40)
print(render(result))
```

Run the built-in demo (Rule 90's Sierpinski triangle, then Rule 110):

```
python cellular_automaton.py
```

## Scope: what "Turing-complete" means here

Cook's actual proof isn't reimplemented — encoding a cyclic tag system's
rules into Rule 110's particle/glider collision dynamics is a
research-level undertaking, not a reasonable scope for this module (on
par with, say, implementing a from-scratch optimizing compiler).

What's demonstrated instead is Rule 110's real qualitative behavior: run
the demo and compare the two outputs. Rule 90 produces a perfect,
entirely predictable Sierpinski triangle (verified in the test suite
against its exact closed-form definition via Pascal's triangle mod 2) —
elegant, but *simple*: fully characterized by a formula, decaying into
pure self-similar structure. Rule 110 produces genuinely complex,
non-repeating structure — persistent "glider"-like diagonal features
that move, collide, and interact unpredictably against a periodic
background. That distinction (Wolfram's Class 3 "chaotic"/simple-fractal
vs. Class 4 "complex"/"edge of chaos") is the actual empirical signature
of what makes universality possible — Class 4 behavior is a necessary
precondition, not the proof itself.

## Tests

```
python -m unittest -v
```

The rule-table generator is checked against the published Rule 110
truth table directly (not just internal self-consistency), and Rule 90's
output is checked against its independent closed-form definition
(C(t, k) mod 2 via Lucas' theorem) across many generations — not just a
handful of hand-picked cases.
