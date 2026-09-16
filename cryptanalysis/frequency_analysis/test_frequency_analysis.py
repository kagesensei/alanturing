import unittest

from frequency_analysis import (
    ALPHABET,
    ENGLISH_LETTER_FREQUENCIES,
    caesar_decrypt,
    caesar_encrypt,
    chi_squared_statistic,
    crack_caesar_cipher,
    frequency_substitution_guess,
    letter_counts,
    letter_frequencies,
)

SAMPLE_ENGLISH_TEXT = (
    "TURING BROKE THE ENIGMA CODE AT BLETCHLEY PARK AND HELPED WIN THE WAR "
    "BY BUILDING MACHINES THAT COULD THINK FASTER THAN ANY HUMAN CODEBREAKER "
    "THE UNIVERSAL MACHINE HE IMAGINED LATER BECAME THE MODERN COMPUTER"
)


class TestLetterStatistics(unittest.TestCase):
    def test_letter_counts_ignores_non_letters(self):
        counts = letter_counts("a1 b2 a3!")
        self.assertEqual(counts["A"], 2)
        self.assertEqual(counts["B"], 1)
        self.assertEqual(counts["C"], 0)

    def test_letter_frequencies_sum_to_100(self):
        frequencies = letter_frequencies(SAMPLE_ENGLISH_TEXT)
        self.assertAlmostEqual(sum(frequencies.values()), 100.0, places=6)

    def test_letter_frequencies_rejects_empty_text(self):
        with self.assertRaises(ValueError):
            letter_frequencies("123!?")

    def test_chi_squared_lower_for_english_like_text(self):
        # A message that's just one repeated rare letter looks nothing
        # like English, so its chi-squared score should be far higher.
        english_score = chi_squared_statistic(SAMPLE_ENGLISH_TEXT)
        unnatural_score = chi_squared_statistic("Q" * len(SAMPLE_ENGLISH_TEXT))
        self.assertLess(english_score, unnatural_score)


class TestCaesarCipher(unittest.TestCase):
    def test_decrypt_reverses_encrypt(self):
        for shift in range(26):
            ciphertext = caesar_encrypt(SAMPLE_ENGLISH_TEXT, shift)
            self.assertEqual(caesar_decrypt(ciphertext, shift), SAMPLE_ENGLISH_TEXT)

    def test_crack_caesar_cipher_recovers_known_shift(self):
        for shift in range(26):
            ciphertext = caesar_encrypt(SAMPLE_ENGLISH_TEXT, shift)
            result = crack_caesar_cipher(ciphertext)
            self.assertEqual(result.shift, shift)
            self.assertEqual(result.plaintext, SAMPLE_ENGLISH_TEXT)

    def test_rejects_ciphertext_with_no_letters(self):
        with self.assertRaises(ValueError):
            crack_caesar_cipher("12345")


class TestFrequencySubstitutionGuess(unittest.TestCase):
    def test_recovers_exact_mapping_when_ranking_matches_english(self):
        # Build a synthetic "plaintext" whose letter *ranking* (not exact
        # percentages) matches ENGLISH_LETTER_FREQUENCIES exactly -- e.g.
        # the most-common English letter appears most often here too --
        # which guarantees the frequency-rank heuristic finds the true
        # substitution, without relying on real text happening to match
        # the reference distribution closely enough.
        ranked = sorted(ALPHABET, key=lambda letter: (-ENGLISH_LETTER_FREQUENCIES[letter], letter))
        plaintext = "".join(letter * (len(ranked) - rank) for rank, letter in enumerate(ranked))

        substitution = dict(zip(ALPHABET, reversed(ALPHABET)))
        ciphertext = "".join(substitution[char] for char in plaintext)

        self.assertEqual(frequency_substitution_guess(ciphertext), plaintext)

    def test_rejects_ciphertext_with_no_letters(self):
        with self.assertRaises(ValueError):
            frequency_substitution_guess("!!!")


if __name__ == "__main__":
    unittest.main(verbosity=2)
