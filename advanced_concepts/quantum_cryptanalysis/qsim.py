"""A minimal pure-Python quantum statevector simulator: just enough
operations (Hadamard, controlled-phase, a reversible classical-function
application, a phase-flip oracle, diffusion, and an exact Quantum Fourier
Transform) to build the textbook Shor's and Grover's algorithm circuits
used elsewhere in this project.

Simulating n qubits costs O(2**n) time and memory (a full statevector),
so this only scales to a handful of qubits -- fine for the toy problem
sizes used here (factoring N <= 35, an 8-item search), which is the
honest limit of what "quantum-inspired" can mean without a real quantum
computer.
"""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass
from typing import Callable


@dataclass
class QuantumRegister:
    """A statevector over `num_qubits` qubits. Amplitudes are indexed by
    the integer whose bit `i` is qubit `i`'s value (qubit 0 = least
    significant bit).
    """

    num_qubits: int
    amplitudes: list[complex]

    @classmethod
    def zero_state(cls, num_qubits: int) -> "QuantumRegister":
        if num_qubits < 1:
            raise ValueError("num_qubits must be at least 1")
        amplitudes = [0j] * (1 << num_qubits)
        amplitudes[0] = 1 + 0j
        return cls(num_qubits, amplitudes)

    def probabilities(self) -> list[float]:
        return [abs(amp) ** 2 for amp in self.amplitudes]

    def marginal_probabilities(self, qubits: tuple[int, ...]) -> dict[int, float]:
        """The probability distribution over just `qubits`' combined
        value, as if only they were measured (every other qubit summed
        out) -- the standard partial-measurement calculation.
        """
        totals: dict[int, float] = {}
        for index, amp in enumerate(self.amplitudes):
            value = _extract_bits(index, qubits)
            totals[value] = totals.get(value, 0.0) + abs(amp) ** 2
        return totals

    def hadamard(self, qubit: int) -> None:
        bit = 1 << qubit
        factor = 1 / math.sqrt(2)
        new_amplitudes = list(self.amplitudes)
        for index, _ in enumerate(self.amplitudes):
            if index & bit:
                continue
            partner = index | bit
            low, high = self.amplitudes[index], self.amplitudes[partner]
            new_amplitudes[index] = factor * (low + high)
            new_amplitudes[partner] = factor * (low - high)
        self.amplitudes = new_amplitudes

    def controlled_phase(self, control: int, target: int, theta: float) -> None:
        mask = (1 << control) | (1 << target)
        factor = cmath.exp(1j * theta)
        for index, amp in enumerate(self.amplitudes):
            if amp and index & mask == mask:
                self.amplitudes[index] = amp * factor

    def apply_xor_function(
        self,
        source_qubits: tuple[int, ...],
        target_qubits: tuple[int, ...],
        func: Callable[[int], int],
    ) -> None:
        """|x>|t> -> |x>|t XOR func(x)>: the standard reversible way to
        fold a classical function into a quantum circuit (self-inverse,
        since XOR-ing the same value twice restores the original `t`).
        """
        new_amplitudes = [0j] * len(self.amplitudes)
        for index, amp in enumerate(self.amplitudes):
            if not amp:
                continue
            x = _extract_bits(index, source_qubits)
            t = _extract_bits(index, target_qubits)
            new_index = _with_bits(index, target_qubits, t ^ func(x))
            new_amplitudes[new_index] += amp
        self.amplitudes = new_amplitudes

    def phase_flip(self, predicate: Callable[[int], bool]) -> None:
        """Flip the sign of every amplitude whose index satisfies
        `predicate` -- the standard Grover "oracle" pattern."""
        for index, amp in enumerate(self.amplitudes):
            if predicate(index):
                self.amplitudes[index] = -amp

    def inversion_about_mean(self) -> None:
        """Grover's diffusion operator over the whole register."""
        mean = sum(self.amplitudes) / len(self.amplitudes)
        self.amplitudes = [2 * mean - amp for amp in self.amplitudes]


def _extract_bits(index: int, qubits: tuple[int, ...]) -> int:
    value = 0
    for position, qubit in enumerate(qubits):
        if index & (1 << qubit):
            value |= 1 << position
    return value


def _with_bits(index: int, qubits: tuple[int, ...], value: int) -> int:
    for position, qubit in enumerate(qubits):
        bit = 1 << qubit
        if value & (1 << position):
            index |= bit
        else:
            index &= ~bit
    return index


def _bit_mask(qubits: tuple[int, ...]) -> int:
    mask = 0
    for qubit in qubits:
        mask |= 1 << qubit
    return mask


def _dft(amplitudes: list[complex], sign: int) -> list[complex]:
    size = len(amplitudes)
    transformed = [0j] * size
    for out_value in range(size):
        total = 0j
        for in_value, amp in enumerate(amplitudes):
            angle = sign * 2 * math.pi * in_value * out_value / size
            total += amp * cmath.exp(1j * angle)
        transformed[out_value] = total / math.sqrt(size)
    return transformed


def apply_qft(register: QuantumRegister, qubits: tuple[int, ...], inverse: bool = False) -> None:
    """Apply the Quantum Fourier Transform (or its inverse) to `qubits`.

    Computed directly from the QFT's mathematical definition -- every
    input amplitude interfering into every output amplitude, per
    X_k = (1/sqrt(N)) * sum_n x_n * exp(+-2*pi*i*n*k/N) -- rather than
    compiled into an elementary gate sequence. Exact, and simple to
    verify directly against that same textbook DFT formula.
    """
    size = 1 << len(qubits)
    sign = 1 if inverse else -1
    qubit_mask = _bit_mask(qubits)

    new_amplitudes = list(register.amplitudes)
    seen_spectators: set[int] = set()
    for base_index, _ in enumerate(register.amplitudes):
        spectator = base_index & ~qubit_mask
        if spectator in seen_spectators:
            continue
        seen_spectators.add(spectator)

        full_indices = [spectator | _with_bits(0, qubits, value) for value in range(size)]
        old = [register.amplitudes[index] for index in full_indices]
        transformed = _dft(old, sign)
        for index, amp in zip(full_indices, transformed):
            new_amplitudes[index] = amp

    register.amplitudes = new_amplitudes
