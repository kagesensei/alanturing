"""A Universal Turing Machine simulator.

Where the basic simulator's `TuringMachine` takes a transition table as a
Python object, a *universal* machine takes its transition table encoded as
data on the tape itself, alongside the input. One fixed `step` function then
simulates whatever machine the tape describes — the defining idea behind
Turing's 1936 universal machine and, later, the stored-program computer.

Tape format
-----------
A single string holds the whole configuration:

    <description>##<left>[<state>:<symbol>]<right>

- `description` is the encoded transition table: `state,symbol>new_state,write,dir;`
  for each rule, concatenated.
- `##` separates the description from the machine being simulated.
- `<left>` / `<right>` are the tape contents on either side of the head.
- `[state:symbol]` is the head marker: the current state and the symbol
  currently under the head, embedded directly in the tape text.

Each step re-scans the description for a rule matching the current
`state,symbol` pair — a linear search performed fresh every step, exactly as
a real universal machine has no separate memory for the table it is
interpreting.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

RESERVED_CHARS = set(",>;#[]:")


class Direction(Enum):
    LEFT = "L"
    RIGHT = "R"
    STAY = "S"


Transition = tuple[str, str, Direction]
TransitionTable = dict[tuple[str, str], Transition]

_MARKER_RE = re.compile(r"\[([^:\]]+):([^\]]*)\]")


@dataclass
class UTMResult:
    accepted: bool
    final_state: str
    tape: str
    steps: int
    halted: bool


def _validate_token(token: str) -> None:
    if not token or RESERVED_CHARS & set(token):
        raise ValueError(
            f"invalid state/symbol token {token!r}: must be non-empty and free of {''.join(sorted(RESERVED_CHARS))!r}"
        )


def encode_transitions(transitions: TransitionTable) -> str:
    """Encode a transition table as the `description` half of a UTM tape."""
    rules = []
    for (state, symbol), (new_state, write_symbol, direction) in transitions.items():
        for token in (state, symbol, new_state, write_symbol):
            _validate_token(token)
        rules.append(f"{state},{symbol}>{new_state},{write_symbol},{direction.value};")
    return "".join(rules)


def build_tape(description: str, input_string: str, initial_state: str, blank_symbol: str = "_") -> str:
    """Combine an encoded description and an input string into one UTM tape."""
    _validate_token(initial_state)
    first_symbol = input_string[0] if input_string else blank_symbol
    rest = input_string[1:]
    return f"{description}##[{initial_state}:{first_symbol}]{rest}"


class UniversalTuringMachine:
    def __init__(self, accept_states: set[str], blank_symbol: str = "_"):
        self.accept_states = accept_states
        self.blank_symbol = blank_symbol

    def step(self, tape: str) -> str | None:
        """Advance a UTM tape by one step, or return None if no rule matches."""
        description, config = tape.split("##", 1)
        match = _MARKER_RE.search(config)
        left, state, symbol, right = config[: match.start()], match.group(1), match.group(2), config[match.end() :]

        rule_prefix = f"{state},{symbol}>"
        start = description.find(rule_prefix)
        if start == -1:
            return None
        end = description.index(";", start)
        new_state, write_symbol, direction = description[start + len(rule_prefix) : end].split(",")

        if direction == Direction.RIGHT.value:
            if not right:
                right = self.blank_symbol
            new_symbol, right = right[0], right[1:]
            left = left + write_symbol
        elif direction == Direction.LEFT.value:
            if not left:
                left = self.blank_symbol
            new_symbol, left = left[-1], left[:-1]
            right = write_symbol + right
        else:
            new_symbol = write_symbol

        return f"{description}##{left}[{new_state}:{new_symbol}]{right}"

    def run(self, tape: str, max_steps: int = 100_000) -> UTMResult:
        steps = 0
        current = tape
        while steps < max_steps:
            next_tape = self.step(current)
            if next_tape is None:
                break
            current = next_tape
            steps += 1

        _, config = current.split("##", 1)
        match = _MARKER_RE.search(config)
        left, state, symbol, right = config[: match.start()], match.group(1), match.group(2), config[match.end() :]
        tape_str = (left + symbol + right).strip(self.blank_symbol) or self.blank_symbol

        return UTMResult(
            accepted=state in self.accept_states,
            final_state=state,
            tape=tape_str,
            steps=steps,
            halted=steps < max_steps,
        )


def binary_increment_transitions() -> TransitionTable:
    """Same machine as basic_simulator's binary_increment_machine, as raw data."""
    return {
        ("right", "0"): ("right", "0", Direction.RIGHT),
        ("right", "1"): ("right", "1", Direction.RIGHT),
        ("right", "_"): ("carry", "_", Direction.LEFT),
        ("carry", "1"): ("carry", "0", Direction.LEFT),
        ("carry", "0"): ("halt", "1", Direction.STAY),
        ("carry", "_"): ("halt", "1", Direction.STAY),
    }


def binary_complement_transitions() -> TransitionTable:
    """Same machine as basic_simulator's binary_complement_machine, as raw data."""
    return {
        ("scan", "0"): ("scan", "1", Direction.RIGHT),
        ("scan", "1"): ("scan", "0", Direction.RIGHT),
        ("scan", "_"): ("halt", "_", Direction.STAY),
    }


if __name__ == "__main__":
    utm = UniversalTuringMachine(accept_states={"halt"})

    increment_description = encode_transitions(binary_increment_transitions())
    for value in ["0", "1", "1011", "111"]:
        tape = build_tape(increment_description, value, initial_state="right")
        result = utm.run(tape)
        print(f"increment({value!r}) -> {result.tape!r}  [{result.steps} steps]")

    complement_description = encode_transitions(binary_complement_transitions())
    for value in ["1010", "1111", "0000"]:
        tape = build_tape(complement_description, value, initial_state="scan")
        result = utm.run(tape)
        print(f"complement({value!r}) -> {result.tape!r}  [{result.steps} steps]")
