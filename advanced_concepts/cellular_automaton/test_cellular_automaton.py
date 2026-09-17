import unittest

from cellular_automaton import rule_table, run


class TestRuleTable(unittest.TestCase):
    def test_rejects_out_of_range_rule(self):
        with self.assertRaises(ValueError):
            rule_table(256)
        with self.assertRaises(ValueError):
            rule_table(-1)

    def test_rule_110_matches_the_published_table(self):
        # The well-known Rule 110 truth table (e.g. Wikipedia's "Rule
        # 110" article): 111->0, 110->1, 101->1, 100->0, 011->1, 010->1,
        # 001->1, 000->0.
        table = rule_table(110)
        expected = {
            (1, 1, 1): 0,
            (1, 1, 0): 1,
            (1, 0, 1): 1,
            (1, 0, 0): 0,
            (0, 1, 1): 1,
            (0, 1, 0): 1,
            (0, 0, 1): 1,
            (0, 0, 0): 0,
        }
        self.assertEqual(table, expected)

    def test_rule_0_maps_everything_to_zero(self):
        table = rule_table(0)
        self.assertTrue(all(not output for output in table.values()))

    def test_rule_255_maps_everything_to_one(self):
        table = rule_table(255)
        self.assertTrue(all(output == 1 for output in table.values()))


class TestRun(unittest.TestCase):
    def test_rejects_negative_steps(self):
        with self.assertRaises(ValueError):
            run(110, [0, 1, 0], steps=-1)

    def test_rejects_empty_initial_state(self):
        with self.assertRaises(ValueError):
            run(110, [], steps=1)

    def test_rejects_non_binary_cells(self):
        with self.assertRaises(ValueError):
            run(110, [0, 2, 0], steps=1)

    def test_zero_steps_returns_only_initial_state(self):
        result = run(110, [1, 0, 1], steps=0)
        self.assertEqual(result.generations, [[1, 0, 1]])

    def test_boundary_cells_treat_out_of_bounds_as_zero(self):
        # Rule 4 (00000100): only neighborhood (0,1,0) -> 1, everything
        # else -> 0. A lone 1 at the left edge (index 0) has left =
        # the implicit out-of-bounds boundary; if that boundary reads
        # as 0 (not 1, not a wraparound), its neighborhood is exactly
        # (0,1,0), so it should turn on next step.
        result = run(4, [1, 0, 0], steps=1)
        self.assertEqual(result.generations[1], [1, 0, 0])

    def test_rule_90_produces_the_sierpinski_triangle(self):
        # Rule 90 is the XOR of the two diagonal neighbors, whose closed
        # form is known exactly: starting from a single 1 at the origin,
        # position x at time t (same parity as t, |x| <= t) is 1 iff
        # C(t, (t+x)/2) is odd (by Lucas' theorem) -- an independent
        # check, not just self-consistency. Extra margin (width well
        # beyond 2*steps) keeps the finite tape's zero-boundary from
        # ever being reachable within the tested range.
        width = 41
        center = width // 2
        seed = [0] * width
        seed[center] = 1
        steps = 15

        result = run(90, seed, steps=steps)

        for t in range(steps + 1):
            for offset in range(-t, t + 1):
                position = center + offset
                expected = not (offset + t) % 2 and _binomial_is_odd(t, (offset + t) // 2)
                self.assertEqual(
                    result.generations[t][position],
                    1 if expected else 0,
                    f"generation {t}, offset {offset}",
                )


def _binomial_is_odd(n: int, k: int) -> bool:
    """True if C(n, k) is odd, via Lucas' theorem: odd iff every bit of
    k is <= the corresponding bit of n (k's binary digits are a
    "sub-pattern" of n's).
    """
    if not 0 <= k <= n:
        return False
    return (n & k) == k


if __name__ == "__main__":
    unittest.main(verbosity=2)
