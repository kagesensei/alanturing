"""Elementary (1D, 2-state, 3-neighbor) cellular automata, per Wolfram's
standard numbering scheme, with a focus on Rule 110 -- proven Turing-
complete by Matthew Cook (2004), via a construction that lets it
simulate cyclic tag systems (themselves Turing-complete).

That proof isn't reimplemented here -- encoding a cyclic tag system's
rules into Rule 110's particle/glider collision dynamics is a research-
level undertaking, not a reasonable scope for this module. What's
demonstrated instead is Rule 110's actual qualitative behavior: unlike
"simple" rules that die out or settle into a short repeating pattern,
Rule 110 produces genuinely complex, non-repeating structure from a
single-cell seed -- the Class 4 ("complex"/"edge of chaos") signature
that's the necessary precondition for universality in the first place.
"""

from __future__ import annotations

from dataclasses import dataclass


def rule_table(rule_number: int) -> dict[tuple[int, int, int], int]:
    """The 8-entry lookup table for elementary CA `rule_number` (0-255),
    per Wolfram's standard numbering: bit `n` of `rule_number` is the
    output for the neighborhood whose 3 bits (left, center, right) equal
    `n` in binary.
    """
    if not 0 <= rule_number <= 255:
        raise ValueError("rule_number must be in [0, 255]")
    table = {}
    for neighborhood in range(8):
        left = (neighborhood >> 2) & 1
        center = (neighborhood >> 1) & 1
        right = neighborhood & 1
        table[(left, center, right)] = (rule_number >> neighborhood) & 1
    return table


@dataclass
class CellularAutomatonResult:
    rule_number: int
    generations: list[list[int]]


def run(rule_number: int, initial_state: list[int], steps: int) -> CellularAutomatonResult:
    """Evolve `initial_state` under elementary CA `rule_number` for
    `steps` generations. Out-of-bounds neighbors are treated as 0 (a
    fixed, non-wrapping boundary) -- the tape stays a finite strip
    rather than growing or wrapping around.
    """
    if steps < 0:
        raise ValueError("steps must be non-negative")
    if not initial_state:
        raise ValueError("initial_state must be non-empty")
    if any(cell not in (0, 1) for cell in initial_state):
        raise ValueError("initial_state must contain only 0s and 1s")

    table = rule_table(rule_number)
    width = len(initial_state)
    generations = [list(initial_state)]
    current = list(initial_state)
    for _ in range(steps):
        current = _next_generation(current, width, table)
        generations.append(current)
    return CellularAutomatonResult(rule_number, generations)


def _next_generation(
    current: list[int], width: int, table: dict[tuple[int, int, int], int]
) -> list[int]:
    next_gen = []
    for i in range(width):
        left = current[i - 1] if i > 0 else 0
        right = current[i + 1] if i < width - 1 else 0
        next_gen.append(table[(left, current[i], right)])
    return next_gen


def render(result: CellularAutomatonResult, alive: str = "#", dead: str = ".") -> str:
    lines = ["".join(alive if cell else dead for cell in gen) for gen in result.generations]
    return "\n".join(lines)


if __name__ == "__main__":
    demo_width = 79
    seed = [0] * demo_width
    seed[demo_width // 2] = 1

    print("Rule 90 (Sierpinski triangle -- simple/fractal, not universal):")
    print(render(run(90, seed, steps=30)))
    print()

    print("Rule 110 (proven Turing-complete by Cook, 2004):")
    print(render(run(110, seed, steps=40)))
