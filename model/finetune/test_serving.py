import unittest

from serve import create_server


class FixtureEngine:
    def complete(self, messages, max_tokens):
        return f"Received {len(messages)} messages, budget {max_tokens}"


class TestAdapterServer(unittest.TestCase):
    def setUp(self):
        self.client = create_server(FixtureEngine(), 'test-model', 'test-key').test_client()
        self.body = {'model': 'test-model', 'messages': [{'role': 'user', 'content': 'Hello'}]}
        self.headers = {'Authorization': 'Bearer test-key'}

    def test_authentication_and_chat_contract(self):
        url = '/v1/chat/completions'
        self.assertEqual(self.client.post(url, json=self.body).status_code, 401)
        response = self.client.post(url, json=self.body, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['choices'][0]['message']['role'], 'assistant')

    def test_wrong_model_and_invalid_messages_fail(self):
        for field, value in (('model', 'wrong'), ('messages', []), ('messages', [None]),
                             ('max_tokens', True), ('max_tokens', 513), ('stream', True)):
            with self.subTest(field=field, value=value):
                body = dict(self.body, **{field: value})
                response = self.client.post('/v1/chat/completions', json=body, headers=self.headers)
                self.assertEqual(response.status_code, 400)
