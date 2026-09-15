"""Unit tests for the palindrome-checking Turing Machine."""

import unittest

from palindrome_turing_machine import PalindromeTuringMachine


class PalindromeAcceptanceTests(unittest.TestCase):
    """The machine must agree with Python's own `s == s[::-1]` check."""

    def setUp(self):
        self.tm = PalindromeTuringMachine()

    def _assert_matches_python(self, candidate):
        result = self.tm.check(candidate)
        expected = candidate == candidate[::-1]
        self.assertEqual(result.is_palindrome, expected, msg=f"mismatch for {candidate!r}")
        self.assertTrue(result.halted)

    def test_empty_string_is_a_palindrome(self):
        self._assert_matches_python("")

    def test_single_character_strings_are_palindromes(self):
        self._assert_matches_python("0")
        self._assert_matches_python("1")

    def test_even_length_palindromes(self):
        self._assert_matches_python("00")
        self._assert_matches_python("0110")
        self._assert_matches_python("011110")

    def test_odd_length_palindromes(self):
        self._assert_matches_python("010")
        self._assert_matches_python("10101")
        self._assert_matches_python("00100")

    def test_even_length_non_palindromes(self):
        self._assert_matches_python("01")
        self._assert_matches_python("0111")
        self._assert_matches_python("011010")

    def test_odd_length_non_palindromes(self):
        self._assert_matches_python("011")
        self._assert_matches_python("10100")

    def test_mismatch_at_the_very_last_pair(self):
        # Everything matches except the outermost pair.
        self._assert_matches_python("100001")

    def test_exhaustive_all_strings_up_to_length_eight(self):
        for length in range(9):
            for value in range(2**length):
                candidate = format(value, f"0{length}b") if length else ""
                self._assert_matches_python(candidate)


class InputValidationTests(unittest.TestCase):
    """The checker should refuse input outside its documented alphabet."""

    def test_non_binary_input_rejected(self):
        with self.assertRaises(ValueError):
            PalindromeTuringMachine().check("01x0")


if __name__ == "__main__":
    unittest.main()
