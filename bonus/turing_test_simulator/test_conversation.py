import unittest

from conversation import Conversation
from evidence import EvidenceLibrary, render_selection


class RecordingClient:
    def __init__(self, response):
        self.responses = list(response) if isinstance(response, (list, tuple)) else [response]
        self.messages = []

    def complete(self, messages):
        self.messages.append(messages)
        return self.responses.pop(0)


class TestEvidenceBoundaries(unittest.TestCase):
    def setUp(self):
        self.library = EvidenceLibrary()

    def test_1936_excludes_future_events_and_spanning_records(self):
        identifiers = {record['claim_id'] for record in self.library.available('turing_1936')}
        self.assertIn('E005', identifiers)
        self.assertNotIn('E006', identifiers)  # Princeton record spans 1936–1938.
        self.assertNotIn('E013', identifiers)
        self.assertNotIn('E018', identifiers)

    def test_every_historical_mode_respects_registry(self):
        for name, persona in self.library.personas.items():
            if persona['is_fictional']:
                continue
            for record in self.library.available(name):
                if record['claim_id'].startswith('E'):
                    self.assertIn(record['claim_id'], persona['known_events'])
                elif record['claim_id'].startswith('I'):
                    self.assertEqual(record['evidence_type'], 'UNKNOWN')

    def test_unknown_is_never_filled_with_a_preference(self):
        text, records = render_selection(['I002'], self.library.available('turing_1950'))
        self.assertIn('does not establish', text)
        self.assertEqual(records[0]['confidence'], 'unknown')
        self.assertEqual(records[0]['claim_category'], 'unknown')
        self.assertEqual(records[0]['source_ids'], [])

    def test_factual_claims_have_resolvable_sources(self):
        for record in self.library.available('turing_a1'):
            if record['evidence_type'] != 'UNKNOWN':
                self.assertTrue(record['source_ids'])
                self.assertTrue(self.library.citations([record]))

    def test_historical_response_uses_persona_style_and_safe_evidence(self):
        client = RecordingClient('I published a paper on computable numbers in 1936.')
        result = Conversation(client).answer(
            'What did Turing publish about computable numbers?', 'turing_1936', [])
        self.assertEqual(result['claims'][0]['source_ids'], ['S004'])
        self.assertIn('SIMULATED_DIALOGUE', result['label'])
        self.assertEqual(result['text'], 'I published a paper on computable numbers in 1936.')
        self.assertEqual(len(client.messages), 1)
        prompt = client.messages[0][0]['content']
        self.assertIn('The simulated speaker is Turing', prompt)
        self.assertIn('say “I published” rather than “your paper”', prompt)
        self.assertIn('dry, whimsical', prompt.lower())
        self.assertIn('E005', prompt)
        self.assertNotIn('E018', prompt)

    def test_simulated_persona_responds_naturally_without_retrieved_records(self):
        client = RecordingClient('Babbage is an interesting subject to explore.')
        result = Conversation(client).answer(
            'What do you think of Charles Babbage?', 'turing_1936', [])
        self.assertEqual(result['claims'], [])
        self.assertEqual(result['sources'], [])
        self.assertEqual(result['text'], 'Babbage is an interesting subject to explore.')
        self.assertEqual(len(client.messages), 1)
        self.assertIn('records retrieved for this turn: []',
                      client.messages[0][0]['content'].lower())

    def test_follow_up_retrieves_evidence_from_prior_turn_context(self):
        history = [{'role': 'user', 'content': 'What did you publish?'},
                   {'role': 'assistant',
                    'content': 'You published On Computable Numbers in 1936.'}]
        client = RecordingClient('I described a simple machine for computation.')
        result = Conversation(client).answer(
            'Tell me about that principle', 'turing_1936', history)
        self.assertEqual([claim['claim_id'] for claim in result['claims']], ['E005'])
        self.assertEqual(client.messages[0][1:], [
            *history, {'role': 'user', 'content': 'Tell me about that principle'},
        ])

    def test_technical_mode_has_no_persona_material(self):
        client = RecordingClient('A tape stores symbols.')
        result = Conversation(client).answer('Explain a tape', 'technical', [])
        self.assertEqual(result['claims'], [])
        self.assertNotIn('SCHOLARLY', client.messages[0][0]['content'])
        self.assertNotIn('E005', client.messages[0][0]['content'])

    def test_unknown_question_abstains_locally(self):
        result = Conversation().answer('Favourite ice cream?', 'turing_1936', [])
        self.assertIn('does not establish', result['text'])
