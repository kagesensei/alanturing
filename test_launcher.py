"""Exercise the mounted chat including its API, assets, invites and exports."""

import unittest

from project_launcher import PROJECTS, create_app
from conversation import Conversation  # pylint: disable=wrong-import-order


class TestLauncher(unittest.TestCase):
    def test_catalogue_and_mounted_chat(self):
        client = create_app(Conversation()).test_client()
        page = client.get('/')
        self.assertEqual(page.status_code, 200)
        for _category, title, _description in PROJECTS:
            self.assertIn(title.encode(), page.data)
        self.assertEqual(page.data.count(b'<a href='), 1)
        self.assertIn(b'The imitation room', client.get('/chat/').data)
        with client.get('/chat/static/judge.js') as asset:
            self.assertEqual(asset.status_code, 200)
        result = client.post('/chat/api/sessions', json={
            'persona': 'technical', 'kind': 'chat',
        }).get_json()
        self.assertTrue(result['invite'].startswith('/chat/respond/'))
        address = '/chat/api/sessions/' + result['id']
        self.assertEqual(client.post(address + '/questions', json={
            'question': 'Explain a Turing machine',
        }).status_code, 200)
        self.assertEqual(client.get(address + '/export').status_code, 200)


if __name__ == '__main__':
    unittest.main()
