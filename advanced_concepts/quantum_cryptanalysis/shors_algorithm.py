"""Shor's algorithm: quantum-accelerated integer factorization, the
textbook demonstration of why a sufficiently large quantum computer
threatens RSA and other factoring-based public-key cryptography (not the
symmetric ciphers covered elsewhere in this project -- Enigma, block
ciphers -- which Grover's algorithm targets instead).

Classical pre/post-processing (choosing a coprime base, continued
fractions, gcd) wraps a genuine quantum period-finding subroutine built
on qsim.py: superpose a "counting" register, fold in modular
exponentiation as a reversible classical function, apply the Quantum
Fourier Transform, and sample the counting register's distribution --
sharply peaked at multiples of 2**n_count / r, letting the period r be
recovered via continued fractions.

Simulating the full statevector costs O(2**(n_count+n_work)), so this
only factors small numbers -- but the quantum subroutine at its core is
exactly the one that scales, on real quantum hardware, to numbers RSA
actually uses.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from fractions import Fraction

from qsim import QuantumRegister, apply_qft


@dataclass
class FactorizationResult:
    factors: tuple[int, int]
    base: int
    period: int
    counting_qubits: int


def _min_counting_qubits(modulus: int) -> int:
    """The standard requirement for reliable continued-fraction period
    recovery: a counting register large enough that 2**n_count >= N**2
    (tight, not the more commonly quoted but more generous 2*bit_length(N)).
    """
    return math.ceil(math.log2(modulus**2))


def _is_perfect_power(number: int) -> bool:
    for exponent in range(2, number.bit_length() + 1):
        root = round(number ** (1 / exponent))
        for candidate in (root - 1, root, root + 1):
            if candidate > 1 and candidate**exponent == number:
                return True
    return False


def _continued_fraction_period(measured: int, counting_size: int, modulus: int) -> int | None:
    """Recover a candidate period from a QFT measurement outcome via its
    continued-fraction convergents -- the standard classical step of
    Shor's algorithm. Returns None if no usable denominator is found.
    """
    if not measured:
        return None
    fraction = Fraction(measured, counting_size).limit_denominator(modulus)
    candidate = fraction.denominator
    return candidate if 0 < candidate < modulus else None


def _quantum_period_guess(
    base: int, modulus: int, counting_qubits: int, work_qubits: int, rng: random.Random
) -> int:
    """Run one shot of the quantum order-finding circuit and sample the
    counting register from its true probability distribution.
    """
    register = QuantumRegister.zero_state(counting_qubits + work_qubits)
    counting = tuple(range(counting_qubits))
    work = tuple(range(counting_qubits, counting_qubits + work_qubits))

    for qubit in counting:
        register.hadamard(qubit)
    register.apply_xor_function(counting, work, lambda x: pow(base, x, modulus))
    apply_qft(register, counting, inverse=False)

    distribution = register.marginal_probabilities(counting)
    outcomes = list(distribution)
    weights = [distribution[outcome] for outcome in outcomes]
    return rng.choices(outcomes, weights=weights, k=1)[0]


def find_period(
    base: int, modulus: int, rng: random.Random | None = None, max_attempts: int = 10
) -> int | None:
    """Quantum period-finding: the smallest r > 0 with base**r % modulus
    == 1, via the simulated circuit above plus continued fractions.
    Returns None if every shot in `max_attempts` fails to yield a usable
    period -- expected occasionally; real Shor's algorithm retries too.
    """
    active_rng = rng if rng is not None else random.Random()
    counting_qubits = _min_counting_qubits(modulus)
    work_qubits = modulus.bit_length()
    counting_size = 1 << counting_qubits

    for _ in range(max_attempts):
        measured = _quantum_period_guess(base, modulus, counting_qubits, work_qubits, active_rng)
        period = _continued_fraction_period(measured, counting_size, modulus)
        if period is not None and pow(base, period, modulus) == 1:
            return period
    return None


def factor(
    modulus: int, rng: random.Random | None = None, max_attempts: int = 20
) -> FactorizationResult:
    """Factor `modulus` (an odd composite that isn't a perfect power)
    using Shor's algorithm.
    """
    if modulus < 4:
        raise ValueError("modulus must be at least 4")
    if not modulus % 2:
        return FactorizationResult((2, modulus // 2), base=2, period=1, counting_qubits=0)
    if _is_perfect_power(modulus):
        raise ValueError(f"{modulus} is a perfect power; Shor's needs a non-prime-power")

    active_rng = rng if rng is not None else random.Random()
    for _ in range(max_attempts):
        base = active_rng.randint(2, modulus - 1)
        shared_factor = math.gcd(base, modulus)
        if shared_factor != 1:
            return FactorizationResult(
                (shared_factor, modulus // shared_factor), base, period=0, counting_qubits=0
            )

        period = find_period(base, modulus, rng=active_rng)
        candidate_factors = _factors_from_period(base, modulus, period)
        if candidate_factors is not None:
            counting_qubits = _min_counting_qubits(modulus)
            return FactorizationResult(candidate_factors, base, period, counting_qubits)

    raise RuntimeError(f"failed to factor {modulus} within {max_attempts} attempts")


def _factors_from_period(base: int, modulus: int, period: int | None) -> tuple[int, int] | None:
    if period is None or period % 2:
        return None
    candidate = pow(base, period // 2, modulus)
    if candidate == modulus - 1:
        return None
    for offset in (-1, 1):
        guess = math.gcd(candidate + offset, modulus)
        if guess not in (1, modulus) and not modulus % guess:
            return (guess, modulus // guess)
    return None


if __name__ == "__main__":
    for target in (15, 21):
        print(f"Factoring {target} with Shor's algorithm...")
        result = factor(target, rng=random.Random(1))
        a, b = result.factors
        print(f"  {target} = {a} x {b}")
        print(
            f"  base={result.base}, period={result.period}, "
            f"counting_qubits={result.counting_qubits}"
        )
