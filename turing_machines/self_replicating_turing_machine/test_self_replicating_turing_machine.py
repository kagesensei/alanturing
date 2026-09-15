"""Unit tests for the self-replicating Turing Machine."""

import unittest

from self_replicating_turing_machine import (
    TapeCopierTuringMachine,
    bits_to_text,
    build_copy_tape,
    self_replication_demo,
    serialize_transitions,
    text_to_bits,
    _build_transitions,
)


class TapeCopierCorrectnessTests(unittest.TestCase):
    """The generic copier must turn 'w#' into exactly 'w#w'."""

    def setUp(self):
        self.tm = TapeCopierTuringMachine()

    def _assert_copies(self, word):
        result = self.tm.run(build_copy_tape(word))
        self.assertTrue(result.accepted)
        self.assertTrue(result.halted)
        self.assertEqual(result.tape, f"{word}#{word}" if word else "#")

    def test_empty_word(self):
        self._assert_copies("")

    def test_single_symbol_words(self):
        self._assert_copies("0")
        self._assert_copies("1")

    def test_repeated_symbol_word(self):
        self._assert_copies("000")
        self._assert_copies("111")

    def test_mixed_word(self):
        self._assert_copies("011010")

    def test_all_words_up_to_length_six(self):
        for length in range(7):
            for value in range(2**length):
                word = format(value, f"0{length}b") if length else ""
                self._assert_copies(word)


class TapeCopierInputValidationTests(unittest.TestCase):
    """The copier should refuse malformed or out-of-alphabet tapes."""

    def test_missing_delimiter_rejected(self):
        with self.assertRaises(ValueError):
            TapeCopierTuringMachine().run("0101")

    def test_multiple_delimiters_rejected(self):
        with self.assertRaises(ValueError):
            TapeCopierTuringMachine().run("01#01#")

    def test_non_binary_word_rejected(self):
        with self.assertRaises(ValueError):
            TapeCopierTuringMachine().run("01x0#")


class BitEncodingRoundTripTests(unittest.TestCase):
    """Text <-> bits helpers must be exact inverses of each other."""

    def test_round_trip_various_text(self):
        for text in ["", "a", "Turing", "0123456789", "!@#$%^&*()"]:
            self.assertEqual(bits_to_text(text_to_bits(text)), text)

    def test_bit_length_is_eight_per_character(self):
        self.assertEqual(len(text_to_bits("abc")), 24)

    def test_malformed_bit_length_rejected(self):
        with self.assertRaises(ValueError):
            bits_to_text("101")


class SerializationDeterminismTests(unittest.TestCase):
    """The transition table must always serialize to the same text."""

    def test_serialization_is_deterministic(self):
        table = _build_transitions()
        self.assertEqual(serialize_transitions(table), serialize_transitions(table))

    def test_serialization_is_pure_ascii(self):
        description = serialize_transitions(_build_transitions())
        self.assertTrue(all(ord(character) < 128 for character in description))


class SelfReplicationTests(unittest.TestCase):
    """The central claim: the copier faithfully duplicates its own genome."""

    def test_copier_reproduces_its_own_transition_table(self):
        report = self_replication_demo()
        self.assertTrue(report.offspring_matches_original)
        self.assertTrue(report.decoded_matches_source)
        self.assertGreater(report.genome_bits, 0)
        self.assertGreater(report.steps, 0)


if __name__ == "__main__":
    unittest.main()
