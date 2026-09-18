import unittest

from benchmark import encrypt_substitution, letter_accuracy, summarize


class TestBenchmarkMetrics(unittest.TestCase):
    def test_accuracy_excludes_unchanged_spaces_and_punctuation(self):
        self.assertEqual(letter_accuracy('AB, CD!', 'AX, CY!'), 0.5)

    def test_accuracy_rejects_missing_or_misaligned_letters(self):
        for expected, actual in (('ABC', 'AB'), (' !', ' !')):
            with self.subTest(expected=expected), self.assertRaises(ValueError):
                letter_accuracy(expected, actual)

    def test_encryption_is_reproducible_and_bijective(self):
        text = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        encrypted = encrypt_substitution(text, 17)
        self.assertEqual(sorted(text), sorted(encrypted))
        self.assertEqual(encrypted, encrypt_substitution(text, 17))
        self.assertNotEqual(encrypted, encrypt_substitution(text, 29))

    def test_summary_keeps_deterministic_baseline_separate(self):
        rows = [{'method': method, 'letter_accuracy': score,
                 'exact_match': score == 1, 'seconds': 0.1}
                for method, score in [('frequency', 0.5), ('genetic', 0.0), ('genetic', 1.0)]]
        result = summarize(rows)
        self.assertEqual(result['frequency']['trials'], 1)
        self.assertEqual(result['genetic']['trials'], 2)
        self.assertEqual(result['genetic']['mean_letter_accuracy'], 0.5)
        self.assertEqual(result['genetic']['exact_recoveries'], 1)
