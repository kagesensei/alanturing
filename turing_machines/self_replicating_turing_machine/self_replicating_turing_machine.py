"""A Turing Machine that copies its own description onto the tape.

Self-replication for a Turing Machine is usually explained through Kleene's
recursion theorem or von Neumann's universal constructor: a machine can be
built that, given a description of itself as data, produces a copy of that
description as part of its output -- the same separation of "instructions"
from "genome" that lets DNA be both executed (transcribed into proteins)
and copied (passed to offspring).

This module builds that idea out of two honest, checkable pieces:

1. `TapeCopierTuringMachine` -- a real, general-purpose single-tape TM that
   copies any binary string `w` from a `w#` tape to `w#w`, using the
   classic mark-and-bounce construction (mark one symbol of `w` consumed,
   walk to the current end of the tape, append the remembered value,
   rewind, repeat).
2. `self_replication_demo()` -- serializes the copier's *own* transition
   table into a bitstring (its "genome"), feeds that genome to the copier
   as the string to duplicate, and confirms the machine produces two
   identical copies of its own description side by side on the tape. The
   copier's code is quite literally treated as data and copied by itself.

Resource bounds
----------------
Copying is the one operation here that is inherently more than a handful
of steps: each of the `n` rounds re-scans up to the whole tape, so the
machine takes on the order of `n^2` steps to copy a length-`n` string.
`run()` still takes a single fixed, finite `max_steps` ceiling -- large
enough for the demonstrations below, but always a constant, never an
open-ended condition -- so a run is always guaranteed to terminate.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

MAX_STEPS_DEFAULT = 20_000_000
CONSUMED_ZERO = "x"
CONSUMED_ONE = "y"
DELIMITER = "#"
BITS_PER_CHARACTER = 8


class Direction(Enum):
    """Which way the tape head moves after a transition."""

    LEFT = "L"
    RIGHT = "R"
    STAY = "S"


Transition = tuple[str, str, Direction]
TransitionTable = dict[tuple[str, str], Transition]


@dataclass
class TMResult:
    """The outcome of running the copier to completion (or cutoff).

    Attributes:
        accepted: True if the machine halted in its accept state.
        tape: The full tape contents, trimmed of surrounding blanks --
            for a successful copy this is `"{w}#{w}"`.
        steps: How many transitions were actually taken.
        halted: True if the machine reached a state with no further
            transition; False if it was cut off by max_steps.
    """

    accepted: bool
    tape: str
    steps: int
    halted: bool


class TapeCopierTuringMachine:
    """Copies the binary string before a single `#` to after it."""

    def __init__(self):
        self.transitions = _build_transitions()
        self.initial_state = "find_unmarked"
        self.accept_states = {"halt"}
        self.blank_symbol = "_"

    def run(self, input_string: str, max_steps: int = MAX_STEPS_DEFAULT) -> TMResult:
        """Run the copier on a `w#` tape for at most `max_steps` steps."""
        if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps < 0:
            raise ValueError("max_steps must be a non-negative integer")
        if input_string.count(DELIMITER) != 1:
            raise ValueError(f"input must contain exactly one {DELIMITER!r} delimiter")
        if any(symbol not in "01" for symbol in input_string.replace(DELIMITER, "")):
            raise ValueError(
                f"the string to copy must be over the alphabet {{0,1}}, got {input_string!r}"
            )

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
        return TMResult(
            accepted=halted and state in self.accept_states,
            tape=self._tape_to_string(tape),
            steps=steps,
            halted=halted,
        )

    def _tape_to_string(self, tape: dict[int, str]) -> str:
        if not tape:
            return self.blank_symbol
        lo, hi = min(tape), max(tape)
        text = "".join(tape.get(i, self.blank_symbol) for i in range(lo, hi + 1))
        return text.strip(self.blank_symbol) or self.blank_symbol


def _build_transitions() -> TransitionTable:
    transitions: TransitionTable = {
        ("find_unmarked", CONSUMED_ZERO): ("find_unmarked", CONSUMED_ZERO, Direction.RIGHT),
        ("find_unmarked", CONSUMED_ONE): ("find_unmarked", CONSUMED_ONE, Direction.RIGHT),
        ("find_unmarked", "0"): ("goto_end_write_0", CONSUMED_ZERO, Direction.RIGHT),
        ("find_unmarked", "1"): ("goto_end_write_1", CONSUMED_ONE, Direction.RIGHT),
        ("find_unmarked", DELIMITER): ("rewind_to_cleanup", DELIMITER, Direction.LEFT),
    }

    for digit in ("0", "1"):
        goto_state = f"goto_end_write_{digit}"
        for symbol in ("0", "1", CONSUMED_ZERO, CONSUMED_ONE, DELIMITER):
            transitions[(goto_state, symbol)] = (goto_state, symbol, Direction.RIGHT)
        transitions[(goto_state, "_")] = ("rewind", digit, Direction.LEFT)

    for symbol in ("0", "1", CONSUMED_ZERO, CONSUMED_ONE, DELIMITER):
        transitions[("rewind", symbol)] = ("rewind", symbol, Direction.LEFT)
    transitions[("rewind", "_")] = ("find_unmarked", "_", Direction.RIGHT)

    for symbol in ("0", "1", CONSUMED_ZERO, CONSUMED_ONE, DELIMITER):
        transitions[("rewind_to_cleanup", symbol)] = ("rewind_to_cleanup", symbol, Direction.LEFT)
    transitions[("rewind_to_cleanup", "_")] = ("sweep_cleanup", "_", Direction.RIGHT)

    transitions[("sweep_cleanup", CONSUMED_ZERO)] = ("sweep_cleanup", "0", Direction.RIGHT)
    transitions[("sweep_cleanup", CONSUMED_ONE)] = ("sweep_cleanup", "1", Direction.RIGHT)
    transitions[("sweep_cleanup", DELIMITER)] = ("halt", DELIMITER, Direction.STAY)

    return transitions


def build_copy_tape(word: str) -> str:
    """Build a `w#` tape ready for `TapeCopierTuringMachine.run()`."""
    return f"{word}{DELIMITER}"


def text_to_bits(text: str) -> str:
    """Encode text as a binary string, `BITS_PER_CHARACTER` bits per character."""
    return "".join(format(ord(character), f"0{BITS_PER_CHARACTER}b") for character in text)


def bits_to_text(bits: str) -> str:
    """Decode a binary string produced by `text_to_bits()` back to text."""
    if len(bits) % BITS_PER_CHARACTER:
        raise ValueError(f"bit string length must be a multiple of {BITS_PER_CHARACTER}")
    characters = [
        chr(int(bits[i : i + BITS_PER_CHARACTER], 2))
        for i in range(0, len(bits), BITS_PER_CHARACTER)
    ]
    return "".join(characters)


def serialize_transitions(transitions: TransitionTable) -> str:
    """Render a transition table as a single deterministic text description.

    This is the machine's "genome". Tape symbols are already single
    characters, so only state names need a code; each is assigned a
    single letter (in sorted order, so the same machine always serializes
    to the same text) and every rule becomes a fixed 5-character record:
    `state, symbol, new_state, write_symbol, direction`. Keeping the
    genome this compact matters in practice -- the copier takes on the
    order of `n^2` steps to duplicate a length-`n` genome.
    """
    source_states = {state for state, _ in transitions}
    target_states = {new_state for new_state, _, _ in transitions.values()}
    all_states = sorted(source_states | target_states)
    state_codes = {state: chr(ord("A") + i) for i, state in enumerate(all_states)}

    records = []
    for (state, symbol), (new_state, write_symbol, direction) in sorted(transitions.items()):
        records.append(
            state_codes[state] + symbol + state_codes[new_state] + write_symbol + direction.value
        )
    return "".join(records)


def genome() -> str:
    """The copier machine's own transition table, encoded as a bitstring."""
    return text_to_bits(serialize_transitions(_build_transitions()))


@dataclass
class SelfReplicationReport:
    """The result of having the copier duplicate its own encoded genome.

    Attributes:
        genome_bits: The length, in bits, of the copier's encoded
            transition table.
        offspring_matches_original: True if the copy the machine produced
            is bit-for-bit identical to the original genome it started
            with.
        decoded_matches_source: True if decoding the copied bits back to
            text reproduces the exact transition-table description that
            was encoded in the first place.
        steps: How many transitions the copier took to complete the copy.
    """

    genome_bits: int
    offspring_matches_original: bool
    decoded_matches_source: bool
    steps: int


def self_replication_demo(max_steps: int = MAX_STEPS_DEFAULT) -> SelfReplicationReport:
    """Feed the copier's own encoded description to itself and verify the copy.

    This is the module's central demonstration: `TapeCopierTuringMachine`
    is a fixed, general-purpose piece of machinery, and the "genome" fed
    to it here happens to be a description of that very machine. Running
    it produces two identical copies of the genome on the tape -- the
    machine has faithfully replicated its own code as data.
    """
    source_description = serialize_transitions(_build_transitions())
    original_genome = text_to_bits(source_description)

    copier = TapeCopierTuringMachine()
    result = copier.run(build_copy_tape(original_genome), max_steps=max_steps)
    if not result.accepted:
        return SelfReplicationReport(len(original_genome), False, False, result.steps)

    written_original, _, offspring = result.tape.partition(DELIMITER)
    offspring_matches_original = written_original == original_genome == offspring
    decoded_matches_source = (
        offspring_matches_original and bits_to_text(offspring) == source_description
    )

    return SelfReplicationReport(
        genome_bits=len(original_genome),
        offspring_matches_original=offspring_matches_original,
        decoded_matches_source=decoded_matches_source,
        steps=result.steps,
    )


if __name__ == "__main__":
    demo_copier = TapeCopierTuringMachine()
    print("Generic copier: 'w#' -> 'w#w'")
    for demo_word in ["", "0", "101", "011010"]:
        demo_result = demo_copier.run(build_copy_tape(demo_word))
        print(
            f"  {demo_word!r:>10} -> {demo_result.tape!r}  "
            f"[{demo_result.steps} steps, halted={demo_result.halted}]"
        )

    print("\nSelf-replication: the copier duplicates its own transition table")
    replication_report = self_replication_demo()
    print(f"  encoded genome size: {replication_report.genome_bits} bits")
    print(f"  steps taken to copy: {replication_report.steps}")
    print(
        "  offspring bit-for-bit identical to original genome: "
        f"{replication_report.offspring_matches_original}"
    )
    print(
        "  offspring decodes back to the exact source description: "
        f"{replication_report.decoded_matches_source}"
    )
