import unittest

from qiskit_backend import grover_search, optimal_iterations


class TestOptimalIterations(unittest.TestCase):
    def test_matches_known_exact_case(self):
        self.assertEqual(optimal_iterations(4, num_marked=1), 1)

    def test_rejects_invalid_counts(self):
        with self.assertRaises(ValueError):
            optimal_iterations(0)


class TestGroverSearch(unittest.TestCase):
    def test_rejects_out_of_range_index(self):
        with self.assertRaises(ValueError):
            grover_search(3, marked_index=8)

    def test_finds_marked_item_with_high_probability(self):
        for num_qubits in (2, 3, 4, 5):
            marked = 3
            result = grover_search(num_qubits, marked_index=marked, shots=1000)
            self.assertEqual(result.marked_index, marked)
            self.assertGreater(result.success_probability, 0.85)

    def test_two_qubit_case_is_near_certain(self):
        result = grover_search(2, marked_index=3, shots=2000)
        self.assertEqual(result.iterations, 1)
        self.assertGreater(result.success_probability, 0.98)


if __name__ == "__main__":
    unittest.main(verbosity=2)
