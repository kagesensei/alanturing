from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import unittest

from model_client import ChatClient, ModelConfig, ModelError


@contextmanager
def model_server(body, status=200):
    received = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):  # pylint: disable=invalid-name
            size = int(self.headers['Content-Length'])
            received.append((json.loads(self.rfile.read(size)), self.headers.get('Authorization')))
            self.send_response(status)
            if status == 302:
                self.send_header('Location', '/unexpected-redirect')
            self.end_headers()
            self.wfile.write(body)

        # Match the stdlib handler's keyword-compatible signature exactly.
        def log_message(self, format, *args):  # pylint: disable=redefined-builtin
            """Suppress fixture access logs; captured requests are asserted below."""

    with ThreadingHTTPServer(('127.0.0.1', 0), Handler) as server:
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            yield f'http://127.0.0.1:{server.server_port}/v1/chat/completions', received
        finally:
            server.shutdown()
            worker.join(timeout=2)


class TestModelTransport(unittest.TestCase):
    def test_actual_http_request_and_bearer_auth(self):
        body = json.dumps({'choices': [{'message': {'content': 'A response'}}]}).encode()
        with model_server(body) as (endpoint, received):
            client = ChatClient(ModelConfig(endpoint, 'fixture-model', 'fixture-key'))
            result = client.complete([{'role': 'user', 'content': 'Hello'}])
        self.assertEqual(result, 'A response')
        self.assertEqual(received[0][0]['model'], 'fixture-model')
        self.assertFalse(received[0][0]['stream'])
        self.assertEqual(received[0][1], 'Bearer fixture-key')

    def test_bad_status_json_shape_size_and_redirect_fail(self):
        cases = ((b'private server error', 500), (b'not json', 200), (b'{}', 200),
                 (b'x' * 65537, 200), (b'', 302))
        for body, status in cases:
            with self.subTest(status=status, size=len(body)), model_server(body, status) as fixture:
                client = ChatClient(ModelConfig(fixture[0], 'fixture-model'))
                with self.assertRaises(ModelError) as failure:
                    client.complete([{'role': 'user', 'content': 'Hello'}])
                self.assertNotIn('private server error', str(failure.exception))

    def test_remote_http_and_embedded_credentials_rejected(self):
        for endpoint in ('http://example.com/chat', 'https://user:secret@example.com/chat',
                         'file:///tmp/model', 'https://example.com/chat?key=secret'):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                ModelConfig(endpoint, 'fixture-model')
