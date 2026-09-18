import unittest

from run_lint import duplicate_fingerprint, is_accepted


class TestLintPolicy(unittest.TestCase):
    def test_line_moves_preserve_fingerprint_but_code_changes_do_not(self):
        original = 'Similar lines\n==one:[1:4]\n==two:[5:8]\nreturn 1'
        moved = original.replace('[1:4]', '[2:5]')
        self.assertEqual(duplicate_fingerprint(original), duplicate_fingerprint(moved))
        self.assertNotEqual(duplicate_fingerprint(original),
                            duplicate_fingerprint(original.replace('return 1', 'return 2')))

    def test_unknown_duplicate_fails(self):
        finding = {'type': 'refactor', 'message-id': 'R0801', 'message': 'new duplication'}
        self.assertFalse(is_accepted(finding, {}))
        self.assertTrue(is_accepted(finding, {duplicate_fingerprint(finding['message']): 'reason'}))

    def test_other_warnings_cannot_be_allowlisted(self):
        finding = {'type': 'warning', 'message-id': 'W0611', 'message': 'unused import'}
        baseline = {duplicate_fingerprint(finding['message']): 'reason'}
        self.assertFalse(is_accepted(finding, baseline))
