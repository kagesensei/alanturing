"""Unit tests for the Non-Deterministic Turing Machine simulator."""

import unittest

from nondeterministic_turing_machine import (
    Direction,
    NondeterministicTuringMachine,
    contains_substring_machine,
)


class ContainsSubstringAcceptanceTests(unittest.TestCase):
    """The NTM should accept exactly the strings containing the pattern."""

    def setUp(self):
        self.tm = contains_substring_machine("101")

    def test_accepts_when_pattern_present(self):
        self.assertTrue(self.tm.run("101").accepted)
        self.assertTrue(self.tm.run("0101").accepted)
        self.assertTrue(self.tm.run("1010").accepted)
        self.assertTrue(self.tm.run("001011").accepted)

    def test_rejects_when_pattern_absent(self):
        self.assertFalse(self.tm.run("").accepted)
        self.assertFalse(self.tm.run("0").accepted)
        self.assertFalse(self.tm.run("111000").accepted)
        self.assertFalse(self.tm.run("000111").accepted)

    def test_reports_halted_and_accepting_tape_on_success(self):
        result = self.tm.run("101")
        self.assertTrue(result.halted)
        self.assertEqual(result.accepting_tape, "101")

    def test_reports_halted_with_no_accepting_tape_on_rejection(self):
        result = self.tm.run("000")
        self.assertTrue(result.halted)
        self.assertIsNone(result.accepting_tape)


class OverlappingAndEdgeMatchTests(unittest.TestCase):
    """Guess-and-verify branches must find matches anywhere, including overlaps."""

    def test_match_at_very_start(self):
        self.assertTrue(contains_substring_machine("11").run("11000").accepted)

    def test_match_at_very_end(self):
        self.assertTrue(contains_substring_machine("11").run("00011").accepted)

    def test_overlapping_occurrences_still_found(self):
        # "111" contains "11" starting at index 0 AND index 1 -- either
        # verification branch accepting is sufficient.
        self.assertTrue(contains_substring_machine("11").run("111").accepted)

    def test_pattern_longer_than_input_rejects(self):
        self.assertFalse(contains_substring_machine("101").run("10").accepted)

    def test_single_symbol_pattern(self):
        tm = contains_substring_machine("1")
        self.assertTrue(tm.run("0001").accepted)
        self.assertFalse(tm.run("0000").accepted)


class BranchingStatisticsTests(unittest.TestCase):
    """Non-determinism should visibly fork into multiple explored branches."""

    def test_multiple_branches_explored_on_repeated_guess_symbol(self):
        tm = contains_substring_machine("11")
        result = tm.run("1111")
        self.assertTrue(result.accepted)
        # Every '1' spawns a verification branch alongside the scan branch,
        # so more than a single linear pass worth of configurations exist.
        self.assertGreater(result.branches_explored, 4)


class InputValidationTests(unittest.TestCase):
    """The builder should refuse patterns outside its documented alphabet."""

    def test_empty_pattern_rejected(self):
        with self.assertRaises(ValueError):
            contains_substring_machine("")

    def test_non_binary_pattern_rejected(self):
        with self.assertRaises(ValueError):
            contains_substring_machine("10x")


class ResourceBoundTests(unittest.TestCase):
    """The search must always terminate, even on a machine that never halts."""

    def test_max_steps_guard_reports_not_halted(self):
        looping_transitions = {
            ("loop", "_"): frozenset({("loop", "_", Direction.RIGHT)}),
        }
        tm = NondeterministicTuringMachine(
            looping_transitions, initial_state="loop", accept_states={"accept"}
        )
        result = tm.run("", max_steps=25)
        self.assertFalse(result.halted)
        self.assertFalse(result.accepted)
        self.assertEqual(result.search_depth, 25)

    def test_max_branches_guard_reports_not_halted(self):
        # A machine that forks into two live branches every single step,
        # neither of which ever reaches an accept state.
        forking_transitions = {
            ("fork", "_"): frozenset(
                {("fork", "_", Direction.RIGHT), ("fork", "_", Direction.LEFT)}
            ),
        }
        tm = NondeterministicTuringMachine(
            forking_transitions, initial_state="fork", accept_states={"accept"}
        )
        result = tm.run("", max_steps=1_000, max_branches=50)
        self.assertFalse(result.halted)
        self.assertFalse(result.accepted)
        self.assertLessEqual(result.branches_explored, 50)


if __name__ == "__main__":
    unittest.main()
