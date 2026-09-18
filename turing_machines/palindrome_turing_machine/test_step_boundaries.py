import unittest

from palindrome_turing_machine import PalindromeTuringMachine


class TestStepBoundaries(unittest.TestCase):
    def test_exact_accept_and_reject_boundaries(self):
        for value, accepted in (("101", True), ("10", False)):
            with self.subTest(value=value):
                complete = PalindromeTuringMachine().check(value)
                exact = PalindromeTuringMachine(max_steps=complete.steps).check(value)
                self.assertTrue(exact.halted)
                self.assertEqual(exact.is_palindrome, accepted)
                cutoff = PalindromeTuringMachine(max_steps=complete.steps - 1).check(value)
                self.assertFalse(cutoff.halted)
                self.assertFalse(cutoff.is_palindrome)

    def test_zero_budget(self):
        result = PalindromeTuringMachine(max_steps=0).check("")
        self.assertEqual(result.steps, 0)
        self.assertFalse(result.halted)

    def test_invalid_budgets(self):
        for value in (-1, 1.5, True, "10"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                PalindromeTuringMachine(max_steps=value)
