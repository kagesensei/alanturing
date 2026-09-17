import random
import unittest

from shors_algorithm import (
    _continued_fraction_period,
    _is_perfect_power,
    _min_counting_qubits,
    factor,
    find_period,
)


class TestIsPerfectPower(unittest.TestCase):
    def test_true_for_perfect_powers(self):
        for number in (4, 8, 9, 16, 25, 27, 32, 49, 64):
            self.assertTrue(_is_perfect_power(number), number)

    def test_false_for_non_perfect_powers(self):
        for number in (2, 3, 5, 6, 7, 10, 15, 21, 35, 97):
            self.assertFalse(_is_perfect_power(number), number)


class TestMinCountingQubits(unittest.TestCase):
    def test_gives_enough_resolution_for_n_squared(self):
        for modulus in (15, 21, 35, 33):
            qubits = _min_counting_qubits(modulus)
            self.assertGreaterEqual(1 << qubits, modulus**2)
            # And it shouldn't be wastefully larger than needed.
            self.assertLess(1 << (qubits - 1), modulus**2)


class TestContinuedFractionPeriod(unittest.TestCase):
    def test_recovers_known_period(self):
        # base=2, N=15: true period is 4, so a measurement near
        # k * counting_size / 4 should recover denominator 4.
        counting_size = 256
        measured = counting_size // 4  # a peak at exactly 1/4
        self.assertEqual(_continued_fraction_period(measured, counting_size, 15), 4)

    def test_zero_measurement_yields_no_period(self):
        self.assertIsNone(_continued_fraction_period(0, 256, 15))


class TestFindPeriod(unittest.TestCase):
    def test_recovers_known_period_of_two_mod_fifteen(self):
        # 2^1=2, 2^2=4, 2^3=8, 2^4=16 mod 15=1 -- true period is 4.
        period = find_period(2, 15, rng=random.Random(1))
        self.assertEqual(period, 4)
        self.assertEqual(pow(2, period, 15), 1)

    def test_recovers_known_period_of_four_mod_fifteen(self):
        # 4^1=4, 4^2=16 mod 15=1 -- true period is 2.
        period = find_period(4, 15, rng=random.Random(1))
        self.assertEqual(period, 2)


class TestFactor(unittest.TestCase):
    def test_rejects_modulus_below_four(self):
        with self.assertRaises(ValueError):
            factor(3)

    def test_rejects_perfect_power(self):
        with self.assertRaises(ValueError):
            factor(9)

    def test_even_modulus_uses_classical_shortcut(self):
        result = factor(4)
        self.assertEqual(sorted(result.factors), [2, 2])
        self.assertEqual(result.period, 1)

    def test_factors_fifteen_across_several_seeds(self):
        for seed in range(5):
            result = factor(15, rng=random.Random(seed))
            self.assertEqual(sorted(result.factors), [3, 5])

    def test_factors_twenty_one(self):
        result = factor(21, rng=random.Random(5))
        self.assertEqual(sorted(result.factors), [3, 7])


if __name__ == "__main__":
    unittest.main(verbosity=2)
