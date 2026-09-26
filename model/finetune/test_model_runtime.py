"""Reject incomplete language weight mappings while allowing unused vision weights."""

import unittest

from model_runtime import check_loaded_weights


class TestCheckpointLoading(unittest.TestCase):
    def test_unused_vision_weights_are_expected(self):
        check_loaded_weights({'missing_keys': [], 'unexpected_keys': [
            'vision_tower.patch_conv.weight', 'multi_modal_projector.linear_1.weight',
        ]})

    def test_missing_mismatched_or_unmapped_language_weights_fail(self):
        reports = (
            {'missing_keys': ['model.layers.0.self_attn.q_proj.weight']},
            {'mismatched_keys': ['model.embed_tokens.weight']},
            {'error_msgs': ['bad checkpoint']},
            {'unexpected_keys': ['language_model.model.layers.0.self_attn.q_proj.weight']},
        )
        for report in reports:
            with self.subTest(report=report), self.assertRaises(ValueError):
                check_loaded_weights(report)


if __name__ == '__main__':
    unittest.main()
