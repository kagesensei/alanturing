import unittest

from simulator_app import create_app
from conversation import Conversation


class TestSimulatorApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app(Conversation())
        self.client = self.app.test_client()

    def start(self, kind='blind'):
        response = self.client.post('/api/sessions',
                                    json={'persona': 'turing_1936', 'kind': kind})
        self.assertEqual(response.status_code, 201)
        result = response.get_json()
        invite = result['invite'].replace('/respond/', '/api/respond/')
        return f"/api/sessions/{result['id']}", invite

    def test_homepage_and_chat(self):
        self.assertIn(b'The imitation room', self.client.get('/').data)
        url, _ = self.start('chat')
        response = self.client.post(url + '/questions', json={'question': 'Computable numbers?'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['rounds'][0]['machine']['sources'])

    def test_blind_round_hides_assignment_until_verdict(self):
        url, invite = self.start()
        pending = self.client.post(url + '/questions',
                                   json={'question': 'Computable numbers?'}).json
        self.assertTrue(pending['rounds'][0]['pending'])
        self.assertNotIn('machine', pending['rounds'][0])
        self.assertNotIn('machine_label', str(self.client.get(url + '/export').json))
        human_view = self.client.get(invite).json
        self.assertNotIn('machine', str(human_view))
        self.client.post(invite, json={'answer': 'My human response.'})
        ready = self.client.get(url).json
        self.assertEqual(set(ready['rounds'][0]), {'question', 'pending', 'A', 'B'})
        result = self.client.post(url + '/verdict', json={'guess': 'A', 'confidence': 70})
        self.assertEqual(result.status_code, 200)
        self.assertIn('machine_label', result.json['verdict'])
        self.assertEqual(result.json['rounds'][0]['human'], 'My human response.')
        response = self.client.post(url + '/questions', json={'question': 'Again?'})
        self.assertEqual(response.status_code, 400)

    def test_invitation_cannot_read_judge_session(self):
        url, invite = self.start()
        token = invite.rsplit('/', 1)[1]
        self.assertEqual(self.client.get('/api/sessions/' + token).status_code, 404)
        judge_token = url.rsplit('/', 1)[1]
        self.assertEqual(self.client.get('/api/respond/' + judge_token).status_code, 404)

    def test_pending_answer_blocks_next_question_and_reveal(self):
        url, _ = self.start()
        self.client.post(url + '/questions', json={'question': 'First?'})
        response = self.client.post(url + '/questions', json={'question': 'Second?'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.post(url + '/verdict', json={'guess': 'A', 'confidence': 50})
                         .status_code, 400)

    def test_rejects_invalid_payloads(self):
        for body in ([], {'persona': {}}, {'kind': 'unknown'}, {'persona': 'not_real'}):
            with self.subTest(body=body):
                self.assertEqual(self.client.post('/api/sessions', json=body).status_code, 400)
        url, _ = self.start('chat')
        for question in ('', 'x' * 2001, None, {}):
            with self.subTest(question_type=type(question)):
                self.assertEqual(self.client.post(url + '/questions', json={'question': question})
                                 .status_code, 400)

    def test_session_limit_and_expiry(self):
        url, _ = self.start('chat')
        for _ in range(6):
            response = self.client.post(url + '/questions', json={'question': 'Hello'})
            self.assertEqual(response.status_code, 200)
        response = self.client.post(url + '/questions', json={'question': 'Seven'})
        self.assertEqual(response.status_code, 400)
        store = self.app.extensions['experiments']
        store.games[url.rsplit('/', 1)[1]].created -= 7201
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_response_is_rendered_as_data_not_html(self):
        url, _ = self.start('chat')
        response = self.client.post(url + '/questions',
                                    json={'question': '<script>alert(1)</script>'})
        self.assertEqual(response.mimetype, 'application/json')
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        with self.client.get('/static/judge.js') as script:
            self.assertIn(b'textContent', script.data)
