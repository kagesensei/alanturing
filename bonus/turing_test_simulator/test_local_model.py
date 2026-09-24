"""Check that missing local weights fail explicitly instead of using demo text."""

from pathlib import Path
import tempfile
import unittest

from conversation import Conversation
from local_model import LocalModelClient
from model_client import ModelError
from simulator_app import create_app


class TestLocalModel(unittest.TestCase):
    def test_missing_adapter_returns_model_error(self):
        with tempfile.TemporaryDirectory() as directory:
            client = LocalModelClient(Path(directory))
            with self.assertRaisesRegex(ModelError, 'Model missing'):
                client.complete([{'role': 'user', 'content': 'Hello'}])
            app = create_app(Conversation(client)).test_client()
            session = app.post('/api/sessions', json={'persona': 'technical'}).json
            response = app.post('/api/sessions/' + session['id'] + '/questions',
                                json={'question': 'Hello'})
            self.assertEqual(response.status_code, 502)
            self.assertIn('Model missing', response.json['error'])


if __name__ == '__main__':
    unittest.main()
