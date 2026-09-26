"""Simple direct chat interface for the local fine-tuned Ministral adapter."""

from pathlib import Path
import re
import secrets
import sys
import traceback

from flask import Flask, jsonify, render_template, request


ROOT = Path(__file__).resolve().parents[2]
SIMULATOR = ROOT / 'bonus' / 'turing_test_simulator'
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SIMULATOR))

from local_model import LocalModelClient  # pylint: disable=wrong-import-position
from model_client import ModelError  # pylint: disable=wrong-import-position
from tools.app_logging import (  # pylint: disable=wrong-import-position
    configure_flask_logging, record_application_error, record_chat_event,
)


SESSION_ID = re.compile(r'[A-Za-z0-9_-]{16,128}\Z')
SYSTEM_PROMPT = (
    'You are turing-a1, a conversational assistant powered by a fine-tuned Ministral model. '
    'Answer the user directly and naturally. You are not Alan Turing and do not claim to be him. '
    'This chat has no retrieval system or historical persona restrictions. Be clear when you are '
    'uncertain and keep answers useful and conversational.'
)


def create_app(client=None):
    """Create a chat app that sends conversation turns directly to local Ministral."""
    app = Flask(__name__, template_folder='chat_templates', static_folder='chat_static')
    app.config['MAX_CONTENT_LENGTH'] = 32_768
    configure_flask_logging(app, 'direct_mistral_chat')
    model_client = client or LocalModelClient()

    @app.get('/')
    def index():
        return render_template('direct_chat.html', backend=model_client.label)

    @app.post('/api/session')
    def new_session():
        session_id = secrets.token_urlsafe(24)
        record_chat_event(session_id, 'chat.started', application='direct_mistral_chat',
                          selected_options={'model': model_client.label,
                                            'mode': 'direct chat, no RAG or persona'})
        return jsonify({'session_id': session_id, 'model': model_client.label}), 201

    @app.post('/api/chat')
    def chat():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            raise ValueError('Expected a JSON object')
        session_id = body.get('session_id')
        messages = body.get('messages')
        if not isinstance(session_id, str) or not SESSION_ID.fullmatch(session_id):
            raise ValueError('Start a new chat session before sending a message')
        validate_messages(messages)
        conversation = [{'role': 'system', 'content': SYSTEM_PROMPT}, *messages[-12:]]
        try:
            answer = model_client.complete(conversation)
        except ModelError as exc:
            log_model_error(session_id, exc)
            raise
        record_chat_event(session_id, 'chat.turn', application='direct_mistral_chat',
                          model=model_client.label, question=messages[-1]['content'],
                          response=answer)
        return jsonify({'response': answer})

    register_errors(app)
    return app


def validate_messages(messages):
    """Accept a bounded user and assistant transcript, excluding client prompts."""
    if not isinstance(messages, list) or not 1 <= len(messages) <= 100:
        raise ValueError('Chat history must contain between 1 and 100 messages')
    for message in messages:
        if (not isinstance(message, dict)
                or message.get('role') not in ('user', 'assistant')
                or not isinstance(message.get('content'), str)
                or not message['content'].strip()
                or len(message['content']) > 4_000):
            raise ValueError('Each chat message must have a user or assistant role and text')
    if messages[-1]['role'] != 'user':
        raise ValueError('The last chat message must be from you')


def log_model_error(session_id, error):
    details = {'level': 'ERROR', 'error_type': type(error).__name__,
               'message': str(error),
               'traceback': ''.join(traceback.format_exception(
                   type(error), error, error.__traceback__))}
    record_chat_event(session_id, 'chat.error', application='direct_mistral_chat', **details)
    record_application_error('direct_mistral_chat', 'model.error', error)


def register_errors(app):
    @app.errorhandler(ValueError)
    def invalid_request(error):
        return jsonify({'error': str(error)}), 400

    @app.errorhandler(ModelError)
    def model_failure(error):
        return jsonify({'error': str(error)}), 502

    @app.errorhandler(Exception)
    def unexpected_failure(error):
        record_application_error('direct_mistral_chat', 'request.error', error,
                                 method=request.method,
                                 route=request.url_rule.rule if request.url_rule else 'unmatched')
        return jsonify({'error': 'An unexpected error occurred'}), 500


if __name__ == '__main__':
    create_app().run(host='127.0.0.1', port=5002, debug=False)
