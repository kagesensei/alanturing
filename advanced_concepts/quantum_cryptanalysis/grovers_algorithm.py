"""Grover's algorithm: quantum search over an unstructured space of
`2**num_qubits` items in O(sqrt(N)) oracle queries, versus O(N)
classically.

Directly relevant to symmetric-key cryptanalysis: a large enough quantum
computer running Grover's search over an n-bit keyspace (e.g. brute-
forcing a block-cipher key, or an Enigma-style rotor/plugboard search)
would need only about sqrt(2**n) tries instead of 2**n -- the reason
NIST's post-quantum guidance recommends doubling symmetric key lengths
to keep the same security margin.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from qsim import QuantumRegister


@dataclass
class GroverResult:
    marked_index: int
    iterations: int
    success_probability: float
    probabilities: list[float]


def optimal_iterations(num_items: int, num_marked: int = 1) -> int:
    """The exact optimal Grover iteration count.

    Grover's rotation angle theta satisfies sin(theta) = sqrt(M/N); after
    k iterations the success probability is sin**2((2k+1)*theta), so the
    optimal k is round(pi/(4*theta) - 1/2). The often-quoted
    round(pi/4 * sqrt(N/M)) is only a large-N/M approximation of this --
    it's wrong for small registers (e.g. it gives 2 iterations for N=4,
    M=1, overshooting; the true optimum there is 1).
    """
    if num_items < 1 or not 1 <= num_marked <= num_items:
        raise ValueError("need 1 <= num_marked <= num_items")
    theta = math.asin(math.sqrt(num_marked / num_items))
    return max(1, round(math.pi / (4 * theta) - 0.5))


def grover_search(num_qubits: int, marked_indices: tuple[int, ...]) -> GroverResult:
    """Search a `2**num_qubits`-item space for any index in
    `marked_indices`, running the optimal number of Grover iterations.
    """
    num_items = 1 << num_qubits
    if not marked_indices or any(not 0 <= i < num_items for i in marked_indices):
        raise ValueError(f"marked_indices must be non-empty indices in [0, {num_items})")

    register = QuantumRegister.zero_state(num_qubits)
    for qubit in range(num_qubits):
        register.hadamard(qubit)

    marked_set = set(marked_indices)
    iterations = optimal_iterations(num_items, len(marked_set))
    for _ in range(iterations):
        register.phase_flip(lambda index: index in marked_set)
        register.inversion_about_mean()

    probabilities = register.probabilities()
    best_index = max(range(num_items), key=lambda index: probabilities[index])
    success_probability = sum(probabilities[index] for index in marked_indices)
    return GroverResult(best_index, iterations, success_probability, probabilities)


if __name__ == "__main__":
    demo_qubits = 6
    keyspace_size = 1 << demo_qubits
    secret_key = 41
    print(f"Searching a {keyspace_size}-item keyspace for key {secret_key}...")

    result = grover_search(demo_qubits, marked_indices=(secret_key,))
    print(f"found: {result.marked_index} in {result.iterations} Grover iteration(s)")
    print(f"success probability: {result.success_probability:.4f}")
    print(f"classical brute force would expect ~{keyspace_size // 2} tries on average")
