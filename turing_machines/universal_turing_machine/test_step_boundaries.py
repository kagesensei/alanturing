import unittest

from universal_turing_machine import (
    UniversalTuringMachine, build_tape, encode_transitions, binary_complement_transitions,
)


class TestStepBoundaries(unittest.TestCase):
    def setUp(self):
        self.machine = UniversalTuringMachine({'halt'})
        description = encode_transitions(binary_complement_transitions())
        self.input_tape = build_tape(description, '01', 'scan')

    def test_exact_budget_reports_halt_and_one_less_reports_cutoff(self):
        complete = self.machine.run(self.input_tape)
        exact = self.machine.run(self.input_tape, max_steps=complete.steps)
        self.assertTrue(exact.halted)
        self.assertTrue(exact.accepted)
        self.assertEqual(exact.tape, complete.tape)
        cutoff = self.machine.run(self.input_tape, max_steps=complete.steps - 1)
        self.assertFalse(cutoff.halted)
        self.assertFalse(cutoff.accepted)

    def test_zero_budget_does_not_execute_transition(self):
        result = self.machine.run(self.input_tape, max_steps=0)
        self.assertEqual(result.steps, 0)
        self.assertFalse(result.halted)
        self.assertFalse(result.accepted)

    def test_invalid_budgets_rejected(self):
        for value in (-1, 1.5, True, "10"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.machine.run(self.input_tape, max_steps=value)
