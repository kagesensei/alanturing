import cmath
import math
import unittest

from qsim import QuantumRegister, apply_qft


def _direct_dft(amplitudes: list[complex], inverse: bool) -> list[complex]:
    """Independent reference implementation of the DFT, straight from
    its definition -- used to check `apply_qft` against, rather than
    trusting the same code that's being tested.
    """
    size = len(amplitudes)
    sign = 1 if inverse else -1
    output = []
    for k in range(size):
        total = 0j
        for n, amp in enumerate(amplitudes):
            total += amp * cmath.exp(sign * 2j * math.pi * n * k / size)
        output.append(total / math.sqrt(size))
    return output


def _assert_states_close(test_case, actual, expected, places=9):
    test_case.assertEqual(len(actual), len(expected))
    for a, e in zip(actual, expected):
        test_case.assertAlmostEqual(a.real, e.real, places=places)
        test_case.assertAlmostEqual(a.imag, e.imag, places=places)


class TestQuantumRegister(unittest.TestCase):
    def test_zero_state_is_all_zero_basis(self):
        register = QuantumRegister.zero_state(3)
        self.assertEqual(register.amplitudes[0], 1 + 0j)
        self.assertTrue(all(not amp for amp in register.amplitudes[1:]))

    def test_hadamard_creates_equal_superposition(self):
        register = QuantumRegister.zero_state(1)
        register.hadamard(0)
        expected = 1 / math.sqrt(2)
        self.assertAlmostEqual(register.amplitudes[0].real, expected)
        self.assertAlmostEqual(register.amplitudes[1].real, expected)

    def test_hadamard_is_self_inverse(self):
        register = QuantumRegister.zero_state(2)
        register.hadamard(0)
        register.hadamard(1)
        original = list(register.amplitudes)
        register.hadamard(0)
        register.hadamard(1)
        _assert_states_close(self, register.amplitudes, [1 + 0j, 0j, 0j, 0j])
        # And a second round-trip from the superposed state recovers it.
        register.hadamard(0)
        register.hadamard(1)
        _assert_states_close(self, register.amplitudes, original)

    def test_controlled_phase_only_affects_both_bits_set(self):
        register = QuantumRegister(2, [1 + 0j, 1 + 0j, 1 + 0j, 1 + 0j])
        register.controlled_phase(control=0, target=1, theta=math.pi)
        # index 3 = 0b11 is the only one with both qubit 0 and qubit 1 set.
        _assert_states_close(self, register.amplitudes, [1 + 0j, 1 + 0j, 1 + 0j, -1 + 0j])

    def test_apply_xor_function_is_self_inverse(self):
        register = QuantumRegister.zero_state(4)
        register.hadamard(0)
        register.hadamard(1)
        original = list(register.amplitudes)

        def func(x):
            return (x * 3 + 1) % 4

        register.apply_xor_function(source_qubits=(0, 1), target_qubits=(2, 3), func=func)
        register.apply_xor_function(source_qubits=(0, 1), target_qubits=(2, 3), func=func)

        _assert_states_close(self, register.amplitudes, original)

    def test_apply_xor_function_entangles_source_and_target(self):
        register = QuantumRegister.zero_state(4)
        register.hadamard(0)
        register.hadamard(1)
        register.apply_xor_function(
            source_qubits=(0, 1), target_qubits=(2, 3), func=lambda x: x
        )
        marginal = register.marginal_probabilities((0, 1, 2, 3))
        # Every nonzero amplitude should have source == target (x XOR'd
        # onto a zero-initialized target equals x itself).
        for index, probability in marginal.items():
            if probability > 1e-12:
                source = index & 0b11
                target = (index >> 2) & 0b11
                self.assertEqual(source, target)

    def test_phase_flip_only_negates_marked_indices(self):
        register = QuantumRegister(2, [1 + 0j, 1 + 0j, 1 + 0j, 1 + 0j])
        register.phase_flip(lambda index: index == 2)
        _assert_states_close(self, register.amplitudes, [1 + 0j, 1 + 0j, -1 + 0j, 1 + 0j])

    def test_single_grover_iteration_on_four_items_finds_marked_item(self):
        # The classic textbook example: 2 qubits (4 items), 1 marked --
        # exactly one Grover iteration amplifies it to probability 1.
        register = QuantumRegister.zero_state(2)
        register.hadamard(0)
        register.hadamard(1)
        register.phase_flip(lambda index: index == 3)
        register.inversion_about_mean()
        probabilities = register.probabilities()
        self.assertAlmostEqual(probabilities[3], 1.0, places=9)
        for index in (0, 1, 2):
            self.assertAlmostEqual(probabilities[index], 0.0, places=9)


class TestApplyQft(unittest.TestCase):
    def test_matches_direct_dft_on_arbitrary_state(self):
        amplitudes = [1 + 0j, 0.5 - 0.2j, 0j, 0.3 + 0.1j, 0j, 0j, 0.4j, 0j]
        norm = math.sqrt(sum(abs(a) ** 2 for a in amplitudes))
        amplitudes = [a / norm for a in amplitudes]

        for inverse in (False, True):
            register = QuantumRegister(3, list(amplitudes))
            apply_qft(register, (0, 1, 2), inverse=inverse)
            expected = _direct_dft(amplitudes, inverse=inverse)
            _assert_states_close(self, register.amplitudes, expected)

    def test_forward_then_inverse_round_trips(self):
        register = QuantumRegister.zero_state(3)
        register.hadamard(0)
        register.controlled_phase(0, 1, math.pi / 3)
        original = list(register.amplitudes)

        apply_qft(register, (0, 1, 2), inverse=False)
        apply_qft(register, (0, 1, 2), inverse=True)

        _assert_states_close(self, register.amplitudes, original)

    def test_qft_of_uniform_superposition_is_zero_state(self):
        register = QuantumRegister.zero_state(3)
        for qubit in range(3):
            register.hadamard(qubit)
        apply_qft(register, (0, 1, 2), inverse=False)
        expected = [1 + 0j] + [0j] * 7
        _assert_states_close(self, register.amplitudes, expected)

    def test_only_transforms_the_named_qubits_spectator_untouched(self):
        register = QuantumRegister.zero_state(3)
        register.hadamard(0)
        register.hadamard(1)
        register.apply_xor_function(source_qubits=(0, 1), target_qubits=(2,), func=lambda x: x & 1)
        before_marginal = register.marginal_probabilities((2,))

        apply_qft(register, (0, 1), inverse=False)

        after_marginal = register.marginal_probabilities((2,))
        for value in (0, 1):
            self.assertAlmostEqual(before_marginal.get(value, 0.0), after_marginal.get(value, 0.0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
