"""A Turing Machine that decides whether a binary string is a palindrome.

The classic single-tape construction works from the outside in: read the
leftmost remaining symbol, mark it consumed, walk all the way to the
current rightmost remaining symbol, and compare. A mismatch rejects
immediately. A match marks that symbol consumed too and the machine walks
back to the new leftmost symbol to start the next round. Running out of
symbols to compare (an empty gap, or a single leftover middle symbol for
an odd-length string) means every pair matched, so the machine accepts.

Consumed cells are overwritten with the marker `#` rather than blanked
out, so the machine can always tell "a symbol I've already matched" apart
from "the true end of the tape" while it re-scans.
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
CONSUMED_MARKER = "#"


@dataclass
class TMResult:
    """The outcome of checking one string for the palindrome property.

    Attributes:
        is_palindrome: True if the machine accepted -- every outside-in
            pair of symbols matched.
        final_state: The state the machine was in when it stopped, useful
            for seeing exactly where a mismatch was detected.
        steps: How many transitions were actually taken.
        halted: True if the machine reached a state with no further
            transition (an accept, or a mismatch); False if it was cut
            off by max_steps.
    """

    is_palindrome: bool
    final_state: str
    steps: int
    halted: bool


class PalindromeTuringMachine:
    """A deterministic single-tape palindrome checker over {0, 1}."""

    def __init__(self, max_steps: int = MAX_STEPS_DEFAULT):
        if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps < 0:
            raise ValueError("max_steps must be a non-negative integer")
        self.transitions = _build_transitions()
        self.max_steps = max_steps

    def check(self, input_string: str) -> TMResult:
        """Decide whether `input_string` (over {0, 1}) is a palindrome."""
        if any(symbol not in "01" for symbol in input_string):
            raise ValueError(f"input must be over the alphabet {{0,1}}, got {input_string!r}")

        tape: dict[int, str] = dict(enumerate(input_string))
        state = "find_left"
        head = 0
        steps = 0

        while steps < self.max_steps:
            symbol = tape.get(head, "_")
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

        halted = (state, tape.get(head, "_")) not in self.transitions
        return TMResult(
            is_palindrome=halted and state == "accept",
            final_state=state,
            steps=steps,
            halted=halted,
        )


def _build_transitions() -> TransitionTable:
    transitions: TransitionTable = {}

    transitions[("find_left", CONSUMED_MARKER)] = ("find_left", CONSUMED_MARKER, Direction.RIGHT)
    transitions[("find_left", "_")] = ("accept", "_", Direction.STAY)

    for digit in ("0", "1"):
        start_state = f"seek_right_expect_{digit}_start"
        scan_state = f"seek_right_expect_{digit}_scan"
        compare_state = f"compare_{digit}"

        transitions[("find_left", digit)] = (start_state, CONSUMED_MARKER, Direction.RIGHT)

        # Nothing left to scan: the symbol just marked was the lone
        # middle character of an odd-length string -- accept outright.
        transitions[(start_state, CONSUMED_MARKER)] = ("accept", CONSUMED_MARKER, Direction.STAY)
        transitions[(start_state, "_")] = ("accept", "_", Direction.STAY)
        for other_digit in ("0", "1"):
            transitions[(start_state, other_digit)] = (scan_state, other_digit, Direction.RIGHT)

        # At least one unconsumed symbol lies ahead: walk to the far
        # boundary (a previously-consumed marker, or the true tape end),
        # then step back onto the last unconsumed symbol to compare it.
        for other_digit in ("0", "1"):
            transitions[(scan_state, other_digit)] = (scan_state, other_digit, Direction.RIGHT)
        transitions[(scan_state, CONSUMED_MARKER)] = (
            compare_state,
            CONSUMED_MARKER,
            Direction.LEFT,
        )
        transitions[(scan_state, "_")] = (compare_state, "_", Direction.LEFT)

        # A match consumes the boundary symbol and rewinds for the next
        # round; a mismatch has no transition, so the machine halts
        # without ever reaching "accept".
        transitions[(compare_state, digit)] = ("rewind", CONSUMED_MARKER, Direction.LEFT)

    transitions[("rewind", "0")] = ("rewind", "0", Direction.LEFT)
    transitions[("rewind", "1")] = ("rewind", "1", Direction.LEFT)
    transitions[("rewind", CONSUMED_MARKER)] = ("rewind", CONSUMED_MARKER, Direction.LEFT)
    transitions[("rewind", "_")] = ("find_left", "_", Direction.RIGHT)

    return transitions


if __name__ == "__main__":
    checker = PalindromeTuringMachine()
    print("Palindrome check over the alphabet {0, 1}:")
    for candidate in ["", "0", "00", "01", "010", "011", "0110", "0111", "10101", "10100"]:
        result = checker.check(candidate)
        verdict = "IS" if result.is_palindrome else "is NOT"
        label = candidate if candidate else "(empty string)"
        print(
            f"  {label!r:>16} {verdict} a palindrome  "
            f"[{result.steps} steps, halted={result.halted}]"
        )
