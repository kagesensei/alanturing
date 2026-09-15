import unittest

from turing_machine import Direction, binary_complement_machine, binary_increment_machine


class BinaryIncrementTests(unittest.TestCase):
    def setUp(self):
        self.tm = binary_increment_machine()

    def test_simple_increment(self):
        self.assertEqual(self.tm.run("0").tape, "1")
        self.assertEqual(self.tm.run("1").tape, "10")

    def test_increment_with_carry(self):
        self.assertEqual(self.tm.run("1011").tape, "1100")

    def test_increment_all_ones_extends_tape(self):
        self.assertEqual(self.tm.run("111").tape, "1000")

    def test_accepts_and_halts(self):
        result = self.tm.run("101")
        self.assertTrue(result.accepted)
        self.assertTrue(result.halted)
        self.assertEqual(result.final_state, "halt")


class BinaryComplementTests(unittest.TestCase):
    def setUp(self):
        self.tm = binary_complement_machine()

    def test_flips_all_bits(self):
        self.assertEqual(self.tm.run("1010").tape, "0101")
        self.assertEqual(self.tm.run("1111").tape, "0000")
        self.assertEqual(self.tm.run("0000").tape, "1111")

    def test_empty_input(self):
        result = self.tm.run("")
        self.assertTrue(result.accepted)
        self.assertEqual(result.tape, "_")


class HaltingTests(unittest.TestCase):
    def test_missing_transition_halts_immediately(self):
        tm = binary_increment_machine()
        tm.transitions.pop(("right", "1"))
        result = tm.run("1")
        self.assertEqual(result.final_state, "right")
        self.assertFalse(result.accepted)

    def test_max_steps_guard_reports_not_halted(self):
        tm = binary_complement_machine()
        # Force an infinite loop: 'scan' on blank goes back to 'scan' instead of halting.
        tm.transitions[("scan", "_")] = ("scan", "_", Direction.RIGHT)
        result = tm.run("1", max_steps=50)
        self.assertFalse(result.halted)
        self.assertEqual(result.steps, 50)


if __name__ == "__main__":
    unittest.main()
