"""Turing Machines that perform unary arithmetic.

Numbers are represented in unary: the value `k` is written as `k` copies
of `"1"` (zero is the empty string). Unary is the natural numeral system
for a Turing Machine to compute in directly, because "add one to a
number" and "remove one from a number" are single-cell edits rather than
a carry-propagating operation, which keeps the machines below small and
their correctness easy to see by hand.

Two machines are provided:

- `unary_addition_machine()` computes `m + n` from a tape of the form
  `1^m + 1^n` (an `m`-run of ones, a `+` separator, an `n`-run of ones).
- `unary_subtraction_machine()` computes the *monus* `max(m - n, 0)` from
  a tape of the form `1^m - 1^n`, using the classic "cross off one pair
  at a time" construction: repeatedly delete one unconsumed digit from
  each side; if the left side runs out first, `m <= n` and the answer is
  0; if the right side runs out first, whatever `1`s remain unconsumed on
  the left are exactly `m - n`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Direction(Enum):
    """Which way the tape head moves after a transition."""

    LEFT = "L"
    RIGHT = "R"
    STAY = "S"


Transition = tuple[str, str, Direction]
TransitionTable = dict[tuple[str, str], Transition]

MAX_STEPS_DEFAULT = 100_000


@dataclass
class TMResult:
    """The outcome of running a deterministic TM to completion (or cutoff).

    Attributes:
        accepted: True if the machine halted in an accept state.
        final_state: The state the machine was in when it stopped.
        tape: The tape contents, trimmed of surrounding blank symbols.
        value: The tape re-read as a unary number (a count of '1's) --
            the arithmetic answer this run computed.
        steps: How many transitions were actually taken.
        halted: True if the machine reached a state with no further
            transition; False if it was cut off by max_steps.
    """

    accepted: bool
    final_state: str
    tape: str
    value: int
    steps: int
    halted: bool


class TuringMachine:
    """A generic deterministic Turing Machine engine."""

    def __init__(
        self,
        transitions: TransitionTable,
        initial_state: str,
        accept_states: set[str],
        blank_symbol: str = "_",
    ):
        self.transitions = transitions
        self.initial_state = initial_state
        self.accept_states = accept_states
        self.blank_symbol = blank_symbol

    def run(self, input_string: str, max_steps: int = MAX_STEPS_DEFAULT) -> TMResult:
        """Run the machine on `input_string` for at most `max_steps` steps."""
        if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps < 0:
            raise ValueError("max_steps must be a non-negative integer")
        tape: dict[int, str] = dict(enumerate(input_string))
        state = self.initial_state
        head = 0
        steps = 0

        while steps < max_steps:
            symbol = tape.get(head, self.blank_symbol)
            key = (state, symbol)
            if key not in self.transitions:
                break

            new_state, write_symbol, direction = self.transitions[key]
            tape[head] = write_symbol
            state = new_state

            if direction is Direction.LEFT:
                head -= 1
            elif direction is Direction.RIGHT:
                head += 1

            steps += 1

        halted = (state, tape.get(head, self.blank_symbol)) not in self.transitions
        tape_str = self._tape_to_string(tape)
        return TMResult(
            accepted=halted and state in self.accept_states,
            final_state=state,
            tape=tape_str,
            value=tape_str.count("1"),
            steps=steps,
            halted=halted,
        )

    def _tape_to_string(self, tape: dict[int, str]) -> str:
        if not tape:
            return self.blank_symbol
        lo, hi = min(tape), max(tape)
        text = "".join(tape.get(i, self.blank_symbol) for i in range(lo, hi + 1))
        return text.strip(self.blank_symbol) or self.blank_symbol


def unary(count: int) -> str:
    """Encode a non-negative integer as a run of `count` `"1"` characters."""
    if count < 0:
        raise ValueError(f"unary numbers must be non-negative, got {count}")
    return "1" * count


def addition_tape(augend: int, addend: int) -> str:
    """Build a `1^augend + 1^addend` tape for `unary_addition_machine()`."""
    return f"{unary(augend)}+{unary(addend)}"


def subtraction_tape(minuend: int, subtrahend: int) -> str:
    """Build a `1^minuend - 1^subtrahend` tape for `unary_subtraction_machine()`."""
    return f"{unary(minuend)}-{unary(subtrahend)}"


def unary_addition_machine() -> TuringMachine:
    """Build a TM computing `m + n` from a `1^m + 1^n` tape.

    The construction relies on a single observation: turning the `+`
    separator into a `1` makes the tape one contiguous run of
    `m + n + 1` ones. Deleting the last one then leaves exactly `m + n`.
    """
    transitions: TransitionTable = {
        ("seek_separator", "1"): ("seek_separator", "1", Direction.RIGHT),
        ("seek_separator", "+"): ("seek_end", "1", Direction.RIGHT),
        ("seek_end", "1"): ("seek_end", "1", Direction.RIGHT),
        ("seek_end", "_"): ("erase_last", "_", Direction.LEFT),
        ("erase_last", "1"): ("halt", "_", Direction.STAY),
    }
    return TuringMachine(transitions, initial_state="seek_separator", accept_states={"halt"})


def unary_subtraction_machine() -> TuringMachine:
    """Build a TM computing `max(m - n, 0)` from a `1^m - 1^n` tape.

    Each round: find one not-yet-consumed digit on the right (marking it
    `y`); if none remains, the right side is exhausted, so whatever
    unconsumed `1`s remain on the left are the answer `m - n`. Otherwise
    find one not-yet-consumed digit on the left (marking it `x`); if none
    remains, the left side ran out first, so `m <= n` and the answer is 0.
    A final sweep converts every leftover marker and the separator to
    blank, leaving only the answer's `1`s (if any) on the tape.
    """
    transitions: TransitionTable = {
        # Cross the left block (original '1's plus already-matched 'x's)
        # to reach the separator, then hunt the right block for a digit
        # still available to match.
        ("pass_left", "1"): ("pass_left", "1", Direction.RIGHT),
        ("pass_left", "x"): ("pass_left", "x", Direction.RIGHT),
        ("pass_left", "-"): ("find_right", "-", Direction.RIGHT),
        ("find_right", "y"): ("find_right", "y", Direction.RIGHT),
        ("find_right", "1"): ("rewind_to_left", "y", Direction.LEFT),
        ("find_right", "_"): ("rewind_to_keep", "_", Direction.LEFT),
        # A right digit was just matched; rewind to the tape start and
        # hunt the left block for a digit to pair it with.
        ("rewind_to_left", "1"): ("rewind_to_left", "1", Direction.LEFT),
        ("rewind_to_left", "x"): ("rewind_to_left", "x", Direction.LEFT),
        ("rewind_to_left", "-"): ("rewind_to_left", "-", Direction.LEFT),
        ("rewind_to_left", "y"): ("rewind_to_left", "y", Direction.LEFT),
        ("rewind_to_left", "_"): ("find_left", "_", Direction.RIGHT),
        ("find_left", "x"): ("find_left", "x", Direction.RIGHT),
        ("find_left", "1"): ("rewind_to_pass", "x", Direction.RIGHT),
        ("find_left", "-"): ("rewind_to_zero", "-", Direction.RIGHT),
        # A pair was matched on both sides; rewind and start the next round.
        ("rewind_to_pass", "1"): ("rewind_to_pass", "1", Direction.LEFT),
        ("rewind_to_pass", "x"): ("rewind_to_pass", "x", Direction.LEFT),
        ("rewind_to_pass", "-"): ("rewind_to_pass", "-", Direction.LEFT),
        ("rewind_to_pass", "y"): ("rewind_to_pass", "y", Direction.LEFT),
        ("rewind_to_pass", "_"): ("pass_left", "_", Direction.RIGHT),
        # Right side ran out: sweep the whole tape, keeping surviving '1's.
        ("rewind_to_keep", "1"): ("rewind_to_keep", "1", Direction.LEFT),
        ("rewind_to_keep", "x"): ("rewind_to_keep", "x", Direction.LEFT),
        ("rewind_to_keep", "-"): ("rewind_to_keep", "-", Direction.LEFT),
        ("rewind_to_keep", "y"): ("rewind_to_keep", "y", Direction.LEFT),
        ("rewind_to_keep", "_"): ("sweep_keep", "_", Direction.RIGHT),
        ("sweep_keep", "1"): ("sweep_keep", "1", Direction.RIGHT),
        ("sweep_keep", "x"): ("sweep_keep", "_", Direction.RIGHT),
        ("sweep_keep", "y"): ("sweep_keep", "_", Direction.RIGHT),
        ("sweep_keep", "-"): ("sweep_keep", "_", Direction.RIGHT),
        ("sweep_keep", "_"): ("halt", "_", Direction.STAY),
        # Left side ran out: the result is 0, so sweep everything to blank.
        ("rewind_to_zero", "1"): ("rewind_to_zero", "1", Direction.LEFT),
        ("rewind_to_zero", "x"): ("rewind_to_zero", "x", Direction.LEFT),
        ("rewind_to_zero", "-"): ("rewind_to_zero", "-", Direction.LEFT),
        ("rewind_to_zero", "y"): ("rewind_to_zero", "y", Direction.LEFT),
        ("rewind_to_zero", "_"): ("sweep_zero", "_", Direction.RIGHT),
        ("sweep_zero", "1"): ("sweep_zero", "_", Direction.RIGHT),
        ("sweep_zero", "x"): ("sweep_zero", "_", Direction.RIGHT),
        ("sweep_zero", "y"): ("sweep_zero", "_", Direction.RIGHT),
        ("sweep_zero", "-"): ("sweep_zero", "_", Direction.RIGHT),
        ("sweep_zero", "_"): ("halt", "_", Direction.STAY),
    }
    return TuringMachine(transitions, initial_state="pass_left", accept_states={"halt"})


if __name__ == "__main__":
    adder = unary_addition_machine()
    print("Unary addition (tape '1^m+1^n' -> '1^(m+n)'):")
    for left_operand, right_operand in [(0, 0), (3, 0), (0, 4), (3, 2), (5, 5)]:
        result = adder.run(addition_tape(left_operand, right_operand))
        print(
            f"  {left_operand} + {right_operand} = {result.value}  "
            f"[tape={result.tape!r}, {result.steps} steps, halted={result.halted}]"
        )

    subtractor = unary_subtraction_machine()
    print("\nUnary subtraction / monus (tape '1^m-1^n' -> '1^max(m-n,0)'):")
    for left_operand, right_operand in [(0, 0), (5, 0), (0, 5), (5, 2), (2, 5), (4, 4)]:
        result = subtractor.run(subtraction_tape(left_operand, right_operand))
        print(
            f"  {left_operand} - {right_operand} = {result.value}  "
            f"[tape={result.tape!r}, {result.steps} steps, halted={result.halted}]"
        )
