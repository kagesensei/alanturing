import unittest

from grovers_algorithm import grover_search, optimal_iterations


class TestOptimalIterations(unittest.TestCase):
    def test_rejects_invalid_counts(self):
        with self.assertRaises(ValueError):
            optimal_iterations(0)
        with self.assertRaises(ValueError):
            optimal_iterations(4, num_marked=5)

    def test_matches_known_exact_case(self):
        # The textbook N=4, M=1 case: exactly 1 iteration is optimal,
        # not the 2 a naive round(pi/4 * sqrt(N/M)) approximation gives.
        self.assertEqual(optimal_iterations(4, num_marked=1), 1)


class TestGroverSearch(unittest.TestCase):
    def test_rejects_out_of_range_marked_index(self):
        with self.assertRaises(ValueError):
            grover_search(3, marked_indices=(8,))

    def test_rejects_empty_marked_indices(self):
        with self.assertRaises(ValueError):
            grover_search(3, marked_indices=())

    def test_finds_marked_item_with_high_probability_across_sizes(self):
        for num_qubits in range(2, 9):
            marked = 3
            result = grover_search(num_qubits, marked_indices=(marked,))
            self.assertEqual(result.marked_index, marked)
            self.assertGreater(result.success_probability, 0.9)

    def test_two_qubit_single_marked_case_is_exact(self):
        # The classic N=4 example: 1 iteration finds the marked item
        # with certainty.
        result = grover_search(2, marked_indices=(3,))
        self.assertEqual(result.iterations, 1)
        self.assertAlmostEqual(result.success_probability, 1.0, places=9)

    def test_probabilities_sum_to_one(self):
        result = grover_search(4, marked_indices=(5,))
        self.assertAlmostEqual(sum(result.probabilities), 1.0, places=9)

    def test_multiple_marked_items_are_jointly_amplified(self):
        result = grover_search(4, marked_indices=(1, 5, 9))
        self.assertGreater(result.success_probability, 0.9)
        self.assertIn(result.marked_index, (1, 5, 9))


if __name__ == "__main__":
    unittest.main(verbosity=2)
