"""Unit tests for the unary-arithmetic Turing Machines."""

import unittest

from arithmetic_turing_machine import (
    addition_tape,
    subtraction_tape,
    unary,
    unary_addition_machine,
    unary_subtraction_machine,
)


class UnaryEncodingTests(unittest.TestCase):
    """The helper encoders must match the documented unary convention."""

    def test_unary_encodes_count_of_ones(self):
        self.assertEqual(unary(0), "")
        self.assertEqual(unary(1), "1")
        self.assertEqual(unary(4), "1111")

    def test_unary_rejects_negative_counts(self):
        with self.assertRaises(ValueError):
            unary(-1)

    def test_addition_tape_format(self):
        self.assertEqual(addition_tape(2, 3), "11+111")
        self.assertEqual(addition_tape(0, 0), "+")

    def test_subtraction_tape_format(self):
        self.assertEqual(subtraction_tape(2, 3), "11-111")
        self.assertEqual(subtraction_tape(0, 0), "-")


class UnaryAdditionTests(unittest.TestCase):
    """m + n for every combination of small operands, checked against int math."""

    def setUp(self):
        self.tm = unary_addition_machine()

    def _assert_sum(self, augend, addend):
        result = self.tm.run(addition_tape(augend, addend))
        self.assertTrue(result.accepted)
        self.assertTrue(result.halted)
        self.assertEqual(result.value, augend + addend)

    def test_both_operands_zero(self):
        self._assert_sum(0, 0)

    def test_left_operand_zero(self):
        self._assert_sum(0, 4)

    def test_right_operand_zero(self):
        self._assert_sum(5, 0)

    def test_two_positive_operands(self):
        self._assert_sum(3, 2)

    def test_larger_operands(self):
        self._assert_sum(11, 13)

    def test_exhaustive_small_grid(self):
        for augend in range(6):
            for addend in range(6):
                self._assert_sum(augend, addend)


class UnarySubtractionTests(unittest.TestCase):
    """m - n (monus) for every combination of small operands, checked against int math."""

    def setUp(self):
        self.tm = unary_subtraction_machine()

    def _assert_monus(self, minuend, subtrahend):
        result = self.tm.run(subtraction_tape(minuend, subtrahend))
        self.assertTrue(result.accepted)
        self.assertTrue(result.halted)
        self.assertEqual(result.value, max(minuend - subtrahend, 0))

    def test_both_operands_zero(self):
        self._assert_monus(0, 0)

    def test_subtracting_zero_is_identity(self):
        self._assert_monus(5, 0)

    def test_minuend_zero_stays_zero(self):
        self._assert_monus(0, 5)

    def test_positive_result(self):
        self._assert_monus(5, 2)

    def test_negative_would_be_result_clamps_to_zero(self):
        self._assert_monus(2, 5)

    def test_equal_operands_give_zero(self):
        self._assert_monus(4, 4)

    def test_exhaustive_small_grid(self):
        for minuend in range(6):
            for subtrahend in range(6):
                self._assert_monus(minuend, subtrahend)


if __name__ == "__main__":
    unittest.main()
