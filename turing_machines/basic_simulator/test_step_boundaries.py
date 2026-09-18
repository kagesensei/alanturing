import unittest

from turing_machine import Direction, TuringMachine, binary_complement_machine


class TestStepBoundaries(unittest.TestCase):
    def setUp(self):
        self.machine = binary_complement_machine()
        self.input_tape = '01'

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

    def test_already_halted_machine_needs_no_steps(self):
        result = TuringMachine({}, 'halt', {'halt'}).run('', max_steps=0)
        self.assertTrue(result.halted)
        self.assertTrue(result.accepted)

    def test_accept_state_with_remaining_transition_is_not_accepted_at_cutoff(self):
        machine = TuringMachine({('accept', '0'): ('accept', '0', Direction.STAY)},
                                'accept', {'accept'})
        result = machine.run('0', max_steps=1)
        self.assertFalse(result.halted)
        self.assertFalse(result.accepted)
