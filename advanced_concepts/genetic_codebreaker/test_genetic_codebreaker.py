import random
import unittest

from genetic_codebreaker import (
    COMMON_WORDS,
    GeneticCrackResult,
    _decrypt,
    _mutate,
    _order_crossover,
    _random_key,
    crack_substitution_cipher,
    fitness,
)
from frequency_analysis import ALPHABET

PLAINTEXT = (
    "THE MACHINE COULD THINK AND THE MACHINE COULD LEARN "
    "THE SECRET CODE WAS BROKEN BY THE TEAM AND THE WAR WAS WON"
)


class TestDecryptAndFitness(unittest.TestCase):
    def test_decrypt_with_identity_key_is_unchanged(self):
        self.assertEqual(_decrypt("HELLO WORLD", tuple(ALPHABET)), "HELLO WORLD")

    def test_fitness_higher_for_recognizable_english(self):
        english_fitness = fitness(PLAINTEXT, tuple(ALPHABET))
        scrambled_key = tuple(reversed(ALPHABET))
        gibberish_fitness = fitness(_decrypt(PLAINTEXT, scrambled_key), tuple(ALPHABET))
        self.assertGreater(english_fitness, gibberish_fitness)

    def test_common_words_are_all_letters_only(self):
        for word in COMMON_WORDS:
            self.assertTrue(word.isalpha())
            self.assertEqual(word, word.upper())


class TestGeneticOperators(unittest.TestCase):
    def test_random_key_is_a_valid_permutation(self):
        key = _random_key(random.Random(0))
        self.assertEqual(sorted(key), sorted(ALPHABET))

    def test_mutate_swaps_exactly_two_positions(self):
        original = tuple(ALPHABET)
        mutated = _mutate(original, random.Random(0))
        differences = [i for i in range(len(original)) if original[i] != mutated[i]]
        self.assertEqual(len(differences), 2)
        self.assertEqual(sorted(mutated), sorted(original))

    def test_order_crossover_produces_valid_permutation(self):
        parent_a = tuple(ALPHABET)
        parent_b = tuple(reversed(ALPHABET))
        child = _order_crossover(parent_a, parent_b, random.Random(0))
        self.assertEqual(sorted(child), sorted(ALPHABET))

    def test_order_crossover_preserves_parent_a_slice(self):
        parent_a = tuple(ALPHABET)
        parent_b = tuple(reversed(ALPHABET))
        # _order_crossover's first (and only) rng draw is the sorted
        # sample of two slice indices -- reproduce it from the same seed
        # to know which slice of parent_a the child must preserve.
        start, end = sorted(random.Random(0).sample(range(len(parent_a)), 2))
        child = _order_crossover(parent_a, parent_b, random.Random(0))
        self.assertEqual(child[start:end], parent_a[start:end])


class TestCrackSubstitutionCipher(unittest.TestCase):
    def test_rejects_empty_ciphertext(self):
        with self.assertRaises(ValueError):
            crack_substitution_cipher("   ")

    def test_rejects_population_size_below_two(self):
        with self.assertRaises(ValueError):
            crack_substitution_cipher("ABCDE", population_size=1)

    def test_rejects_elite_count_out_of_range(self):
        with self.assertRaises(ValueError):
            crack_substitution_cipher("ABCDE", population_size=10, elite_count=10)

    def test_recovers_known_atbash_substitution(self):
        substitution = dict(zip(ALPHABET, reversed(ALPHABET)))
        ciphertext = "".join(substitution.get(char, char) for char in PLAINTEXT)

        result = crack_substitution_cipher(ciphertext, rng=random.Random(1))

        self.assertIsInstance(result, GeneticCrackResult)
        self.assertEqual(result.plaintext, PLAINTEXT)

    def test_elite_keeps_best_key_from_regressing(self):
        substitution = dict(zip(ALPHABET, reversed(ALPHABET)))
        ciphertext = "".join(substitution.get(char, char) for char in PLAINTEXT)

        result = crack_substitution_cipher(
            ciphertext,
            population_size=40,
            generations=60,
            elite_count=4,
            rng=random.Random(2),
        )

        self.assertGreaterEqual(result.fitness, fitness(ciphertext, tuple(ALPHABET)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
