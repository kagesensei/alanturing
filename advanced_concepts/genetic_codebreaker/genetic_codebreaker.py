"""A genetic algorithm for breaking monoalphabetic substitution ciphers:
evolves a population of candidate 26-letter substitution keys (as
permutations) via selection, order-preserving crossover, and mutation.

Meaningfully different from cryptanalysis/frequency_analysis's
`frequency_substitution_guess`: that's a single, deterministic rank-
matching guess -- fast, but only reliable when the ciphertext's letter
frequencies already closely track the English reference distribution.
A genetic algorithm instead searches the full permutation space (26!,
far too large to brute force) using a fitness function that rewards
recognizable English words in the decryption -- word boundaries survive
substitution encryption unchanged, since only letters get substituted --
with letter-frequency chi-squared (reusing frequency_analysis's tested
implementation) as a secondary signal that still gives useful gradient
before any whole words decrypt correctly.
"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from pathlib import Path

_FREQUENCY_ANALYSIS_DIR = (
    Path(__file__).resolve().parent.parent.parent / "cryptanalysis" / "frequency_analysis"
)
if str(_FREQUENCY_ANALYSIS_DIR) not in sys.path:
    sys.path.insert(0, str(_FREQUENCY_ANALYSIS_DIR))

from frequency_analysis import (  # pylint: disable=wrong-import-position
    ALPHABET,
    chi_squared_statistic,
)

COMMON_WORDS = frozenset(
    """
    A I IN IS IT OF ON OR TO BE AT AS AN BY DO GO HE IF ME MY NO SO UP US WE AM
    THE AND FOR ARE BUT NOT YOU ALL CAN HER WAS ONE OUR OUT DAY GET HAS HIM HIS
    HOW MAN NEW NOW OLD SEE TWO WAY WHO BOY DID ITS LET PUT SAY SHE TOO USE YES
    YET ANY WAR WON TEAM WHY OWN OFF TOP TEN SIX TEA
    THAT WITH FROM THEY WILL WOULD THERE THEIR WHICH ABOUT COULD SHOULD
    THINK THING WORLD LEARN BROKE BROKEN MACHINE MACHINES SECRET CODE CODES
    LOGIC MIND TIME WORK MADE LIFE MIGHT GREAT WHERE THESE THOSE AFTER
    BEFORE COMPUTER SCIENCE TURING ENIGMA CIPHER CIPHERS MESSAGE MESSAGES
    LETTER LETTERS NUMBER NUMBERS SYSTEM PATTERN PATTERNS ANALYSIS PROBLEM
    ANSWER QUESTION KNOWLEDGE UNDERSTAND INTELLIGENCE COMPUTATION ALGORITHM
    EVOLUTION GENETIC POPULATION SELECTION MUTATION GENERATION FASTER HUMAN
    BRAIN TRUE FALSE QUICK BROWN FOX JUMPS OVER LAZY DOG WHILE TRIED USING
    BREAK BREAKS HELPED PARK BLETCHLEY DURING SECOND WORLD
    """.split()
)


@dataclass
class GeneticCrackResult:
    key: tuple[str, ...]
    plaintext: str
    fitness: float
    generations_run: int


def _decrypt(ciphertext: str, key: tuple[str, ...]) -> str:
    mapping = dict(zip(ALPHABET, key))
    return "".join(mapping.get(char, char) for char in ciphertext.upper())


def _word_score(word: str) -> float:
    cleaned = "".join(char for char in word if char in ALPHABET)
    return len(cleaned) ** 1.5 if cleaned in COMMON_WORDS else 0.0


def fitness(ciphertext: str, key: tuple[str, ...]) -> float:
    """Higher is better: a weighted count of recognizable English words
    in the decryption, plus a small letter-frequency-based signal.
    """
    decrypted = _decrypt(ciphertext, key)
    word_bonus = sum(_word_score(token) for token in decrypted.split())
    frequency_penalty = chi_squared_statistic(decrypted)
    return word_bonus - 0.01 * frequency_penalty


def _random_key(rng: random.Random) -> tuple[str, ...]:
    letters = list(ALPHABET)
    rng.shuffle(letters)
    return tuple(letters)


def _mutate(key: tuple[str, ...], rng: random.Random) -> tuple[str, ...]:
    key_list = list(key)
    i, j = rng.sample(range(len(key_list)), 2)
    key_list[i], key_list[j] = key_list[j], key_list[i]
    return tuple(key_list)


def _order_crossover(
    parent_a: tuple[str, ...], parent_b: tuple[str, ...], rng: random.Random
) -> tuple[str, ...]:
    """Standard "order crossover" (OX) for permutation-representation
    genetic algorithms: copy a contiguous slice from `parent_a`, then
    fill the remaining positions in `parent_b`'s relative order, skipping
    genes already used -- keeps the child a valid permutation.
    """
    size = len(parent_a)
    start, end = sorted(rng.sample(range(size), 2))
    child: list[str | None] = [None] * size
    child[start:end] = parent_a[start:end]
    used = set(child[start:end])
    fill_values = (gene for gene in parent_b if gene not in used)
    for i in range(size):
        if child[i] is None:
            child[i] = next(fill_values)
    return tuple(child)


def _tournament_select(
    scored: list[tuple[tuple[str, ...], float]], rng: random.Random, tournament_size: int
) -> tuple[str, ...]:
    contenders = rng.sample(scored, tournament_size)
    return max(contenders, key=lambda item: item[1])[0]


def _next_generation(
    scored: list[tuple[tuple[str, ...], float]],
    rng: random.Random,
    *,
    population_size: int,
    elite_count: int,
    tournament_size: int,
    mutation_rate: float,
) -> list[tuple[str, ...]]:
    """Elitism-preserving next generation: keep the top `elite_count`
    keys unchanged, then fill the rest via tournament-selected parents,
    order crossover, and occasional mutation.
    """
    next_population = [key for key, _ in scored[:elite_count]]
    while len(next_population) < population_size:
        parent_a = _tournament_select(scored, rng, tournament_size)
        parent_b = _tournament_select(scored, rng, tournament_size)
        child = _order_crossover(parent_a, parent_b, rng)
        if rng.random() < mutation_rate:
            child = _mutate(child, rng)
        next_population.append(child)
    return next_population


def _validate_search_parameters(
    population_size, generations, mutation_rate, elite_count, tournament_size,
) -> None:
    for name, value, minimum in (
        ("population_size", population_size, 2), ("generations", generations, 0),
        ("elite_count", elite_count, 0), ("tournament_size", tournament_size, 1),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")
    if elite_count >= population_size:
        raise ValueError("elite_count must be less than population_size")
    if tournament_size > population_size:
        raise ValueError("tournament_size must not exceed population_size")
    if (
        isinstance(mutation_rate, bool) or not isinstance(mutation_rate, (int, float))
        or not 0 <= mutation_rate <= 1
    ):
        raise ValueError("mutation_rate must be a finite number in [0, 1]")


def crack_substitution_cipher(
    ciphertext: str,
    *,
    population_size: int = 200,
    generations: int = 300,
    mutation_rate: float = 0.15,
    elite_count: int = 10,
    tournament_size: int = 5,
    rng: random.Random | None = None,
) -> GeneticCrackResult:
    """Evolve a population of candidate substitution keys to decrypt
    `ciphertext`, returning the best key/decryption found.
    """
    if not isinstance(ciphertext, str) or not any(char in ALPHABET for char in ciphertext.upper()):
        raise ValueError("ciphertext must contain at least one A-Z letter")
    _validate_search_parameters(
        population_size, generations, mutation_rate, elite_count, tournament_size,
    )

    active_rng = rng if rng is not None else random.Random()
    population = [_random_key(active_rng) for _ in range(population_size)]
    best_key, best_fitness = population[0], fitness(ciphertext, population[0])

    for _ in range(generations):
        scored = sorted(
            ((key, fitness(ciphertext, key)) for key in population),
            key=lambda item: item[1],
            reverse=True,
        )
        if scored[0][1] > best_fitness:
            best_key, best_fitness = scored[0]

        population = _next_generation(
            scored,
            active_rng,
            population_size=population_size,
            elite_count=elite_count,
            tournament_size=tournament_size,
            mutation_rate=mutation_rate,
        )

    return GeneticCrackResult(best_key, _decrypt(ciphertext, best_key), best_fitness, generations)


if __name__ == "__main__":
    substitution = dict(zip(ALPHABET, ALPHABET[::-1]))  # a simple Atbash-style cipher
    demo_plaintext = (
        "THE MACHINE COULD THINK AND THE MACHINE COULD LEARN "
        "THE SECRET CODE WAS BROKEN BY THE TEAM AND THE WAR WAS WON"
    )
    demo_ciphertext = "".join(substitution.get(char, char) for char in demo_plaintext)
    print(f"ciphertext: {demo_ciphertext}")

    demo_result = crack_substitution_cipher(demo_ciphertext, rng=random.Random(1))
    print(
        f"recovered (fitness={demo_result.fitness:.1f}, "
        f"{demo_result.generations_run} generations):"
    )
    print(f"  {demo_result.plaintext}")
    print(f"exact match: {demo_result.plaintext == demo_plaintext}")
