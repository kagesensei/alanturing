"""A deterministic Turing Machine simulator.

Models the classic 5-tuple-plus-tape formulation: an infinite tape, a head,
a current state, and a transition function mapping (state, symbol) pairs to
(new_state, write_symbol, direction).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum


class Direction(Enum):
    LEFT = "L"
    RIGHT = "R"
    STAY = "S"


Transition = tuple[str, str, Direction]
TransitionTable = dict[tuple[str, str], Transition]


@dataclass
class TMResult:
    accepted: bool
    final_state: str
    tape: str
    steps: int
    halted: bool


class TuringMachine:
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

    def run(self, input_string: str, max_steps: int = 100_000) -> TMResult:
        tape: dict[int, str] = defaultdict(lambda: self.blank_symbol)
        for i, symbol in enumerate(input_string):
            tape[i] = symbol

        state = self.initial_state
        head = 0
        steps = 0

        while steps < max_steps:
            symbol = tape[head]
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

        halted = steps < max_steps
        return TMResult(
            accepted=state in self.accept_states,
            final_state=state,
            tape=self._tape_to_string(tape),
            steps=steps,
            halted=halted,
        )

    def _tape_to_string(self, tape: dict[int, str]) -> str:
        if not tape:
            return ""
        lo, hi = min(tape), max(tape)
        return "".join(tape[i] for i in range(lo, hi + 1)).strip(self.blank_symbol) or self.blank_symbol


def binary_increment_machine() -> TuringMachine:
    """Increments a binary number on the tape by 1 (e.g. "1011" -> "1100")."""
    transitions: TransitionTable = {
        ("right", "0"): ("right", "0", Direction.RIGHT),
        ("right", "1"): ("right", "1", Direction.RIGHT),
        ("right", "_"): ("carry", "_", Direction.LEFT),
        ("carry", "1"): ("carry", "0", Direction.LEFT),
        ("carry", "0"): ("halt", "1", Direction.STAY),
        ("carry", "_"): ("halt", "1", Direction.STAY),
    }
    return TuringMachine(transitions, initial_state="right", accept_states={"halt"})


def binary_complement_machine() -> TuringMachine:
    """Flips every bit on the tape (e.g. "1010" -> "0101")."""
    transitions: TransitionTable = {
        ("scan", "0"): ("scan", "1", Direction.RIGHT),
        ("scan", "1"): ("scan", "0", Direction.RIGHT),
        ("scan", "_"): ("halt", "_", Direction.STAY),
    }
    return TuringMachine(transitions, initial_state="scan", accept_states={"halt"})


if __name__ == "__main__":
    increment = binary_increment_machine()
    for value in ["0", "1", "1011", "111"]:
        result = increment.run(value)
        print(f"increment({value!r}) -> {result.tape!r}  [{result.steps} steps]")

    complement = binary_complement_machine()
    for value in ["1010", "1111", "0000"]:
        result = complement.run(value)
        print(f"complement({value!r}) -> {result.tape!r}  [{result.steps} steps]")
