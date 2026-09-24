import copy
from pathlib import Path
import tempfile
import unittest

from evaluate import score_examples
from prepare_data import generate_examples, partition, validate_splits, write_dataset
from train import ensure_lengths
from training_config import HERE, load_config, load_splits, preflight


class FixtureClient:
    def __init__(self, response):
        self.response = response
        self.messages = []

    def complete(self, messages):
        self.messages = messages
        return self.response


class FixtureTokenizer:
    @staticmethod
    def apply_chat_template(_messages, tokenize):
        if not tokenize:
            raise ValueError('This fixture only returns tokens')
        return list(range(20))


class TestTrainingData(unittest.TestCase):
    def test_engine_answers_match_independent_arithmetic(self):
        for row in generate_examples():
            family, key = row['meta']['group'].split(':', 1)
            if family == 'binary_increment':
                self.assertEqual(row['meta']['answer'], format(int(key, 2) + 1, 'b'))
            elif family == 'unary_addition':
                left, right = map(int, key.split(':'))
                self.assertEqual(row['meta']['answer'], str(left + right))

    def test_no_group_or_prompt_leakage(self):
        splits = partition(generate_examples())
        validate_splits(splits)
        for rows in splits.values():
            self.assertEqual({row['meta']['family'] for row in rows},
                             {'binary_increment', 'unary_addition', 'caesar_decryption'})
        contaminated = copy.deepcopy(splits)
        contaminated['test'].append(contaminated['train'][0])
        with self.assertRaisesRegex(ValueError, 'leakage'):
            validate_splits(contaminated)

    def test_deterministic_files_and_preflight(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            first = write_dataset(directory)
            self.assertEqual(first, write_dataset(directory))
            splits = load_splits(directory)
            self.assertEqual(sum(map(len, splits.values())), 1018)
            report = preflight(load_config(HERE / 'config.json'), directory)
            self.assertIn('no GPU training', report['status'])

    def test_persona_sources_are_not_in_training_corpus(self):
        for row in generate_examples():
            self.assertNotIn('persona/', row['meta']['source'])
            self.assertIn('not a historical persona', row['prompt'][0]['content'])

    def test_answer_mismatch_rejected(self):
        splits = partition(generate_examples())
        splits['train'][0]['meta']['answer'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'verified answer'):
            validate_splits(splits)

    def test_overlength_answers_cannot_be_silently_truncated(self):
        splits = partition(generate_examples())
        with self.assertRaisesRegex(ValueError, 'truncate'):
            ensure_lengths(FixtureTokenizer(), splits, 10)
        ensure_lengths(FixtureTokenizer(), splits, 20)

    def test_evaluation_never_sends_reference_answer(self):
        row = next(generate_examples())
        client = FixtureClient('Explanation\nANSWER: ' + row['meta']['answer'])
        report = score_examples(client, [row])
        self.assertTrue(report['predictions'][0]['correct'])
        self.assertEqual(client.messages, row['prompt'])
        self.assertTrue(all(message['role'] != 'assistant' for message in client.messages))

    def test_incorrect_generation_is_scored_as_failure(self):
        row = next(generate_examples())
        report = score_examples(FixtureClient('ANSWER: incorrect'), [row])
        self.assertFalse(report['predictions'][0]['correct'])
