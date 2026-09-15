import unittest

from universal_turing_machine import (
    Direction,
    UniversalTuringMachine,
    binary_complement_transitions,
    binary_increment_transitions,
    build_tape,
    encode_transitions,
)


class BinaryIncrementTests(unittest.TestCase):
    def setUp(self):
        self.utm = UniversalTuringMachine(accept_states={"halt"})
        self.description = encode_transitions(binary_increment_transitions())

    def run_utm(self, value):
        tape = build_tape(self.description, value, initial_state="right")
        return self.utm.run(tape)

    def test_simple_increment(self):
        self.assertEqual(self.run_utm("0").tape, "1")
        self.assertEqual(self.run_utm("1").tape, "10")

    def test_increment_with_carry(self):
        self.assertEqual(self.run_utm("1011").tape, "1100")

    def test_increment_all_ones_extends_tape(self):
        self.assertEqual(self.run_utm("111").tape, "1000")

    def test_accepts_and_halts(self):
        result = self.run_utm("101")
        self.assertTrue(result.accepted)
        self.assertTrue(result.halted)
        self.assertEqual(result.final_state, "halt")


class BinaryComplementTests(unittest.TestCase):
    def setUp(self):
        self.utm = UniversalTuringMachine(accept_states={"halt"})
        self.description = encode_transitions(binary_complement_transitions())

    def run_utm(self, value):
        tape = build_tape(self.description, value, initial_state="scan")
        return self.utm.run(tape)

    def test_flips_all_bits(self):
        self.assertEqual(self.run_utm("1010").tape, "0101")
        self.assertEqual(self.run_utm("1111").tape, "0000")

    def test_empty_input(self):
        result = self.run_utm("")
        self.assertTrue(result.accepted)
        self.assertEqual(result.tape, "_")


class SameTapeDifferentMachineTests(unittest.TestCase):
    """The same UniversalTuringMachine instance simulates different machines
    just by handing it a different description — the point of a UTM."""

    def test_one_utm_runs_two_different_programs(self):
        utm = UniversalTuringMachine(accept_states={"halt"})

        increment_tape = build_tape(
            encode_transitions(binary_increment_transitions()), "111", initial_state="right"
        )
        complement_tape = build_tape(
            encode_transitions(binary_complement_transitions()), "111", initial_state="scan"
        )

        self.assertEqual(utm.run(increment_tape).tape, "1000")
        self.assertEqual(utm.run(complement_tape).tape, "000")


class EncodingTests(unittest.TestCase):
    def test_rejects_reserved_characters_in_tokens(self):
        bad_transitions = {("a,b", "0"): ("a", "0", Direction.RIGHT)}
        with self.assertRaises(ValueError):
            encode_transitions(bad_transitions)

    def test_build_tape_rejects_reserved_characters_in_initial_state(self):
        with self.assertRaises(ValueError):
            build_tape("s,0>s,0,S;", "0", initial_state="bad;state")


class HaltingTests(unittest.TestCase):
    def test_missing_transition_halts_immediately(self):
        utm = UniversalTuringMachine(accept_states={"halt"})
        transitions = binary_increment_transitions()
        del transitions[("right", "1")]
        tape = build_tape(encode_transitions(transitions), "1", initial_state="right")

        result = utm.run(tape)
        self.assertEqual(result.final_state, "right")
        self.assertFalse(result.accepted)

    def test_max_steps_guard_reports_not_halted(self):
        utm = UniversalTuringMachine(accept_states={"halt"})
        transitions = binary_complement_transitions()
        # Force an infinite loop: 'scan' on blank goes back to 'scan' instead of halting.
        transitions[("scan", "_")] = ("scan", "_", Direction.RIGHT)
        tape = build_tape(encode_transitions(transitions), "1", initial_state="scan")

        result = utm.run(tape, max_steps=50)
        self.assertFalse(result.halted)
        self.assertEqual(result.steps, 50)


if __name__ == "__main__":
    unittest.main()
