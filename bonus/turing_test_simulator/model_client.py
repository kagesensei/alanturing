"""Small chat-completions transport with bounded requests and explicit configuration."""

from dataclasses import dataclass
import json
import os
from urllib import error, parse, request


class ModelError(RuntimeError):
    """A configured model could not produce a valid response."""


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ModelError('Model endpoint redirects are not supported')


@dataclass(frozen=True)
class ModelConfig:
    endpoint: str
    model: str
    api_key: str = ''
    timeout: int = 30

    def __post_init__(self):
        url = parse.urlsplit(self.endpoint)
        local = url.hostname in ('localhost', '127.0.0.1', '::1')
        if url.username or url.password or url.query or url.fragment:
            raise ValueError('Endpoint must not contain URL credentials, queries, or fragments')
        if (url.scheme not in ('http', 'https') or not url.hostname
                or (url.scheme == 'http' and not local)):
            raise ValueError('Endpoint must be HTTPS or loopback HTTP without URL credentials')
        if not self.model.strip() or not 1 <= self.timeout <= 120:
            raise ValueError('Model name and a 1–120 second timeout are required')

    @classmethod
    def from_environment(cls):
        endpoint = os.environ.get('TURING_MODEL_ENDPOINT', '')
        if not endpoint:
            return None
        return cls(endpoint, os.environ.get('TURING_MODEL_ID', ''),
                   os.environ.get('TURING_MODEL_API_KEY', ''))


class ChatClient:
    def __init__(self, config: ModelConfig):
        self.config = config

    def complete(self, messages: list[dict]) -> str:
        payload = json.dumps({'model': self.config.model, 'messages': messages,
                              'max_tokens': 512, 'temperature': 0.2, 'stream': False}).encode()
        headers = {'Content-Type': 'application/json'}
        if self.config.api_key:
            headers['Authorization'] = f'Bearer {self.config.api_key}'
        outgoing = request.Request(self.config.endpoint, data=payload,
                                   headers=headers, method='POST')
        try:
            with request.build_opener(NoRedirect()).open(
                outgoing, timeout=self.config.timeout,
            ) as response:
                body = response.read(65_537)
            if len(body) > 65_536:
                raise ModelError('Model response exceeded 64 KiB')
            document = json.loads(body)
            content = document['choices'][0]['message']['content']
            if not isinstance(content, str) or not content.strip() or len(content) > 8000:
                raise ModelError('Model returned empty or oversized text')
            return content
        except (error.URLError, TimeoutError, OSError) as exc:
            raise ModelError('Model endpoint unavailable; check configuration and server') from exc
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise ModelError('Model endpoint returned an invalid chat response') from exc
