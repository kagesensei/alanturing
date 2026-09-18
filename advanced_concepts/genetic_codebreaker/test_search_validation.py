import random
import unittest

from genetic_codebreaker import crack_substitution_cipher


class TestSearchValidation(unittest.TestCase):
    def test_invalid_search_parameters(self):
        cases = (
            {"generations": -1}, {"generations": 1.5}, {"generations": True},
            {"population_size": 2.5}, {"population_size": True},
            {"elite_count": -1}, {"elite_count": 1.5},
            {"tournament_size": 0}, {"tournament_size": 201}, {"tournament_size": 1.5},
            {"mutation_rate": -0.1}, {"mutation_rate": 1.1},
            {"mutation_rate": float("nan")}, {"mutation_rate": float("inf")},
            {"mutation_rate": "0.5"}, {"mutation_rate": True},
        )
        for parameters in cases:
            with self.subTest(parameters=parameters), self.assertRaises(ValueError):
                crack_substitution_cipher("HELLO WORLD", **parameters)

    def test_rejects_text_without_ascii_letters(self):
        for value in ("123 !", "", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                crack_substitution_cipher(value)

    def test_valid_boundary_parameters(self):
        for rate in (0, 1):
            result = crack_substitution_cipher(
                "HELLO WORLD", population_size=2, elite_count=0, tournament_size=2,
                generations=0, mutation_rate=rate, rng=random.Random(1),
            )
            self.assertEqual(result.generations_run, 0)
            self.assertEqual(len(result.key), 26)
