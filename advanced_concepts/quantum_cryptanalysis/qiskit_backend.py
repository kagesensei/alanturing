"""Grover's algorithm built with real Qiskit (IBM's quantum SDK), run on
the Aer simulator -- an alternative backend alongside the hand-rolled
statevector simulator in qsim.py/grovers_algorithm.py, exposing the same
kind of result so the two are directly comparable.

Scope note: Shor's algorithm is *not* reimplemented here. Modern Qiskit
no longer ships a turnkey Shor's primitive (it was removed from
qiskit-algorithms) -- a "real Qiskit Shor's" would mean hand-building the
same modular-exponentiation-plus-QFT circuit already built, gate by gate,
in shors_algorithm.py, just on a different substrate. That's duplicated
engineering effort without new educational content. Grover's, by
contrast, is exactly the circuit shape Qiskit is built to express
directly, so it's the meaningful comparison point.

Requires `qiskit` and `qiskit-aer` (see requirements.txt).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


@dataclass
class GroverResult:
    marked_index: int
    iterations: int
    success_probability: float
    counts: dict[str, int]


def optimal_iterations(num_items: int, num_marked: int = 1) -> int:
    """Same exact formula as the hand-rolled backend -- see
    grovers_algorithm.optimal_iterations for why the naive
    round(pi/4 * sqrt(N/M)) approximation isn't used.
    """
    if num_items < 1 or not 1 <= num_marked <= num_items:
        raise ValueError("need 1 <= num_marked <= num_items")
    theta = math.asin(math.sqrt(num_marked / num_items))
    return max(1, round(math.pi / (4 * theta) - 0.5))


def _marked_bits(num_qubits: int, marked_index: int) -> str:
    """Bit `i` of the result is qubit `i`'s value in `marked_index`."""
    return format(marked_index, f"0{num_qubits}b")[::-1]


def _phase_flip_marked(circuit: QuantumCircuit, num_qubits: int, marked_index: int) -> None:
    """Flip the sign of the |marked_index> basis state: X-gate every
    qubit that should be 0 (so the target maps to |11...1>), apply a
    multi-controlled Z, then undo the X gates.
    """
    bits = _marked_bits(num_qubits, marked_index)
    zero_qubits = [qubit for qubit, bit in enumerate(bits) if bit == "0"]
    for qubit in zero_qubits:
        circuit.x(qubit)
    circuit.h(num_qubits - 1)
    circuit.mcx(list(range(num_qubits - 1)), num_qubits - 1)
    circuit.h(num_qubits - 1)
    for qubit in zero_qubits:
        circuit.x(qubit)


def _diffusion(circuit: QuantumCircuit, num_qubits: int) -> None:
    circuit.h(range(num_qubits))
    circuit.x(range(num_qubits))
    circuit.h(num_qubits - 1)
    circuit.mcx(list(range(num_qubits - 1)), num_qubits - 1)
    circuit.h(num_qubits - 1)
    circuit.x(range(num_qubits))
    circuit.h(range(num_qubits))


def grover_search(num_qubits: int, marked_index: int, shots: int = 2000) -> GroverResult:
    """Search a `2**num_qubits`-item space for `marked_index`, running
    the optimal number of Grover iterations on Qiskit's Aer simulator.
    """
    num_items = 1 << num_qubits
    if not 0 <= marked_index < num_items:
        raise ValueError(f"marked_index must be in [0, {num_items})")

    circuit = QuantumCircuit(num_qubits, num_qubits)
    circuit.h(range(num_qubits))

    iterations = optimal_iterations(num_items)
    for _ in range(iterations):
        _phase_flip_marked(circuit, num_qubits, marked_index)
        _diffusion(circuit, num_qubits)
    circuit.measure(range(num_qubits), range(num_qubits))

    counts = AerSimulator().run(circuit, shots=shots).result().get_counts()
    best_bits = max(counts, key=counts.get)
    best_index = int(best_bits, 2)
    marked_bits = _marked_bits(num_qubits, marked_index)[::-1]
    success_probability = counts.get(marked_bits, 0) / shots

    return GroverResult(best_index, iterations, success_probability, counts)


if __name__ == "__main__":
    demo_qubits = 6
    keyspace_size = 1 << demo_qubits
    secret_key = 41
    print(f"Searching a {keyspace_size}-item keyspace for key {secret_key} (Qiskit backend)...")

    demo_result = grover_search(demo_qubits, secret_key)
    print(f"found: {demo_result.marked_index} in {demo_result.iterations} Grover iteration(s)")
    print(f"success probability: {demo_result.success_probability:.4f}")
