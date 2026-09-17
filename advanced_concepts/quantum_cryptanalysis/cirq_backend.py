"""Grover's algorithm built with real Cirq (Google's quantum SDK) --
an alternative backend alongside the hand-rolled statevector simulator
in qsim.py/grovers_algorithm.py, and the Qiskit backend in
qiskit_backend.py, exposing the same kind of result so all three are
directly comparable. See qiskit_backend.py's module docstring for why
Shor's algorithm isn't reimplemented here too -- the same reasoning
applies.

Cirq's convention for `cirq.measure(*qubits, ...)` + `histogram()`
treats the *first*-listed qubit as the most significant bit -- the
opposite of this project's "qubit 0 = least significant bit" convention
used everywhere else (qsim.py, qiskit_backend.py). `_line_qubit` below
maps logical qubit index `i` to the Cirq qubit that ends up as bit `i`
of the measured integer, so the public API stays consistent regardless.

Requires `cirq` (see requirements.txt).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import cirq


@dataclass
class GroverResult:
    marked_index: int
    iterations: int
    success_probability: float
    counts: dict[int, int]


def optimal_iterations(num_items: int, num_marked: int = 1) -> int:
    """Same exact formula as the hand-rolled backend -- see
    grovers_algorithm.optimal_iterations for why the naive
    round(pi/4 * sqrt(N/M)) approximation isn't used.
    """
    if num_items < 1 or not 1 <= num_marked <= num_items:
        raise ValueError("need 1 <= num_marked <= num_items")
    theta = math.asin(math.sqrt(num_marked / num_items))
    return max(1, round(math.pi / (4 * theta) - 0.5))


def _line_qubit(qubits: list[cirq.LineQubit], logical_index: int) -> cirq.LineQubit:
    """Map "logical qubit `logical_index`" (bit `logical_index` of the
    eventual measured integer) to Cirq's corresponding LineQubit.
    """
    return qubits[len(qubits) - 1 - logical_index]


def _phase_flip_marked(qubits: list[cirq.LineQubit], marked_index: int) -> list[cirq.Operation]:
    """Flip the sign of |marked_index>: X-gate every logical qubit that
    should be 0, apply a multi-controlled Z, then undo the X gates.
    """
    num_qubits = len(qubits)
    bits = format(marked_index, f"0{num_qubits}b")[::-1]
    zero_qubits = [_line_qubit(qubits, i) for i, bit in enumerate(bits) if bit == "0"]
    ordered = [_line_qubit(qubits, i) for i in range(num_qubits)]
    ops = [cirq.X(qubit) for qubit in zero_qubits]
    ops.append(cirq.Z(ordered[-1]).controlled_by(*ordered[:-1]))
    ops.extend(cirq.X(qubit) for qubit in zero_qubits)
    return ops


def _diffusion(qubits: list[cirq.LineQubit]) -> list[cirq.Operation]:
    ops = [cirq.H(qubit) for qubit in qubits]
    ops.extend(cirq.X(qubit) for qubit in qubits)
    ops.append(cirq.Z(qubits[-1]).controlled_by(*qubits[:-1]))
    ops.extend(cirq.X(qubit) for qubit in qubits)
    ops.extend(cirq.H(qubit) for qubit in qubits)
    return ops


def grover_search(num_qubits: int, marked_index: int, repetitions: int = 2000) -> GroverResult:
    """Search a `2**num_qubits`-item space for `marked_index`, running
    the optimal number of Grover iterations on Cirq's simulator.
    """
    num_items = 1 << num_qubits
    if not 0 <= marked_index < num_items:
        raise ValueError(f"marked_index must be in [0, {num_items})")

    qubits = cirq.LineQubit.range(num_qubits)
    circuit = cirq.Circuit(cirq.H(qubit) for qubit in qubits)

    iterations = optimal_iterations(num_items)
    for _ in range(iterations):
        circuit.append(_phase_flip_marked(qubits, marked_index))
        circuit.append(_diffusion(qubits))
    circuit.append(cirq.measure(*qubits, key="result"))

    result = cirq.Simulator().run(circuit, repetitions=repetitions)
    counts = dict(result.histogram(key="result"))
    best_index = max(counts, key=counts.get)
    success_probability = counts.get(marked_index, 0) / repetitions

    return GroverResult(best_index, iterations, success_probability, counts)


if __name__ == "__main__":
    demo_qubits = 6
    keyspace_size = 1 << demo_qubits
    secret_key = 41
    print(f"Searching a {keyspace_size}-item keyspace for key {secret_key} (Cirq backend)...")

    demo_result = grover_search(demo_qubits, secret_key)
    print(f"found: {demo_result.marked_index} in {demo_result.iterations} Grover iteration(s)")
    print(f"success probability: {demo_result.success_probability:.4f}")
