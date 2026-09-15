"""A Non-Deterministic Turing Machine (NTM) simulator.

A deterministic Turing Machine's transition function maps each
`(state, symbol)` pair to exactly one `(new_state, write_symbol,
direction)`. A *non-deterministic* machine relaxes that to a *set* of
possible transitions per pair: at each step, every applicable transition
is taken at once, conceptually forking the computation into parallel
branches. The machine accepts an input if *any* branch reaches an accept
state; it rejects only if every branch has died out (no branch is still
live) without ever accepting.

This module simulates that fork-everywhere semantics honestly, by tracking
the whole frontier of live branches (a breadth-first search over
configurations) rather than by first converting to an equivalent
deterministic machine, so the branching factor and search cost are visible
in the reported statistics.

Resource bounds
----------------
Because branches can multiply every step, the search is given two fixed,
finite ceilings up front -- a maximum search depth (`max_steps`) and a
maximum number of distinct configurations to ever visit (`max_branches`).
Both loops in `run` are bounded by these constants alone (never by a
condition that could itself grow unboundedly), so a run always terminates
in bounded time even on a machine that never halts.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

MAX_BRANCHES_DEFAULT = 20_000
MAX_STEPS_DEFAULT = 1_000


class Direction(Enum):
    """Which way the tape head moves after a transition."""

    LEFT = "L"
    RIGHT = "R"
    STAY = "S"


Transition = tuple[str, str, Direction]
NTMTransitionTable = dict[tuple[str, str], frozenset[Transition]]
SparseTape = tuple[tuple[int, str], ...]


@dataclass
class NTMResult:
    """The outcome of simulating an NTM on one input string.

    Attributes:
        accepted: True if some branch reached an accept state.
        search_depth: How many BFS levels (steps) were explored before a
            decision was reached, or before the search was cut off.
        branches_explored: Total distinct configurations visited across
            every branch -- a direct measure of how much "parallel work"
            the non-determinism did.
        accepting_tape: The tape contents left behind by the accepting
            branch, or None if the machine rejected or was cut off.
        halted: True if the search reached a definite accept/reject
            verdict; False if it was cut off by max_steps or
            max_branches with no verdict reached yet.
    """

    accepted: bool
    search_depth: int
    branches_explored: int
    accepting_tape: str | None
    halted: bool


@dataclass(frozen=True)
class _Config:
    """One immutable snapshot of a single branch: state, head, and tape."""

    state: str
    head: int
    tape: SparseTape


def _string_to_tape(input_string: str, blank_symbol: str) -> SparseTape:
    return tuple((i, symbol) for i, symbol in enumerate(input_string) if symbol != blank_symbol)


def _tape_to_dict(tape: SparseTape) -> dict[int, str]:
    return dict(tape)


def _dict_to_tape(cells: dict[int, str], blank_symbol: str) -> SparseTape:
    return tuple(sorted((i, symbol) for i, symbol in cells.items() if symbol != blank_symbol))


def _tape_to_string(tape: SparseTape, blank_symbol: str) -> str:
    if not tape:
        return blank_symbol
    indices = [i for i, _ in tape]
    lo, hi = min(indices), max(indices)
    cells = _tape_to_dict(tape)
    text = "".join(cells.get(i, blank_symbol) for i in range(lo, hi + 1))
    return text.strip(blank_symbol) or blank_symbol


class NondeterministicTuringMachine:
    """Simulates a Turing Machine whose transition table may branch."""

    def __init__(
        self,
        transitions: NTMTransitionTable,
        initial_state: str,
        accept_states: set[str],
        blank_symbol: str = "_",
    ):
        self.transitions = transitions
        self.initial_state = initial_state
        self.accept_states = accept_states
        self.blank_symbol = blank_symbol

    def _successors(self, config: _Config) -> list[_Config]:
        cells = _tape_to_dict(config.tape)
        symbol = cells.get(config.head, self.blank_symbol)
        moves = self.transitions.get((config.state, symbol), frozenset())

        children = []
        for new_state, write_symbol, direction in moves:
            new_cells = dict(cells)
            new_cells[config.head] = write_symbol
            if direction is Direction.LEFT:
                new_head = config.head - 1
            elif direction is Direction.RIGHT:
                new_head = config.head + 1
            else:
                new_head = config.head
            new_tape = _dict_to_tape(new_cells, self.blank_symbol)
            children.append(_Config(new_state, new_head, new_tape))
        return children

    def run(
        self,
        input_string: str,
        max_steps: int = MAX_STEPS_DEFAULT,
        max_branches: int = MAX_BRANCHES_DEFAULT,
    ) -> NTMResult:
        """Explore every branch breadth-first until one accepts or all die out.

        `max_steps` bounds the search depth and `max_branches` bounds the
        total number of distinct configurations ever visited; both are
        fixed, finite ceilings so this method always returns.
        """
        start = _Config(self.initial_state, 0, _string_to_tape(input_string, self.blank_symbol))
        frontier = [start]
        visited = {start}
        branches_explored = 1

        for depth in range(max_steps + 1):
            for config in frontier:
                if config.state in self.accept_states:
                    tape_str = _tape_to_string(config.tape, self.blank_symbol)
                    return NTMResult(True, depth, branches_explored, tape_str, True)

            if not frontier:
                return NTMResult(False, depth, branches_explored, None, True)

            if depth == max_steps:
                break

            next_frontier = []
            for config in frontier:
                for child in self._successors(config):
                    if child in visited:
                        continue
                    visited.add(child)
                    next_frontier.append(child)
                    branches_explored += 1
                    if branches_explored >= max_branches:
                        return NTMResult(False, depth + 1, branches_explored, None, False)
            frontier = next_frontier

        return NTMResult(False, max_steps, branches_explored, None, False)


def contains_substring_machine(
    pattern: str, blank_symbol: str = "_"
) -> NondeterministicTuringMachine:
    """Build an NTM that accepts binary strings containing `pattern`.

    This is the canonical "guess and verify" use of non-determinism: while
    scanning left to right, the machine may *at any position* branch into
    a verification path that commits to "the match starts here" -- the
    scanning branch keeps looking elsewhere at the same time. A branch
    that guesses wrong simply has no further transition and dies quietly;
    it does not cause rejection unless every branch dies.

    Args:
        pattern: A non-empty string over the alphabet {0, 1} to search for.
        blank_symbol: The tape's blank symbol.

    Raises:
        ValueError: If pattern is empty or contains a symbol outside {0, 1}.
    """
    if not pattern or any(symbol not in "01" for symbol in pattern):
        raise ValueError(f"pattern must be a non-empty string over {{0,1}}, got {pattern!r}")

    alphabet = ("0", "1")
    transitions: dict[tuple[str, str], set[Transition]] = defaultdict(set)

    for symbol in alphabet:
        transitions[("scan", symbol)].add(("scan", symbol, Direction.RIGHT))

    pattern_length = len(pattern)
    if pattern_length == 1:
        transitions[("scan", pattern[0])].add(("accept", pattern[0], Direction.STAY))
    else:
        transitions[("scan", pattern[0])].add(("verify-1", pattern[0], Direction.RIGHT))
        for i in range(1, pattern_length - 1):
            transitions[(f"verify-{i}", pattern[i])].add(
                (f"verify-{i + 1}", pattern[i], Direction.RIGHT)
            )
        last_symbol = pattern[pattern_length - 1]
        transitions[(f"verify-{pattern_length - 1}", last_symbol)].add(
            ("accept", last_symbol, Direction.STAY)
        )

    frozen_transitions = {key: frozenset(value) for key, value in transitions.items()}
    return NondeterministicTuringMachine(
        frozen_transitions,
        initial_state="scan",
        accept_states={"accept"},
        blank_symbol=blank_symbol,
    )


if __name__ == "__main__":
    for needle in ["101", "11", "000"]:
        machine = contains_substring_machine(needle)
        print(f"\nNTM searching for {needle!r} in a binary string:")
        for candidate in ["0", "1010", "11111", "000000", "0110100"]:
            result = machine.run(candidate)
            verdict = "CONTAINS" if result.accepted else "does not contain"
            print(
                f"  {candidate!r:>10} {verdict} {needle!r}  "
                f"(search depth {result.search_depth}, "
                f"{result.branches_explored} branch(es) explored, "
                f"halted={result.halted})"
            )
