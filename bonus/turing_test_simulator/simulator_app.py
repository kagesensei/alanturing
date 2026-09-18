"""Local Flask interface for evidence-aware chat and blind comparison sessions."""

from flask import Flask, jsonify, render_template, request

from conversation import Conversation
from experiment import ExperimentStore
from model_client import ChatClient, ModelConfig, ModelError


def request_object():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ValueError('Expected a JSON object')
    return body


def create_app(conversation=None):
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 16_384
    if conversation is None:
        config = ModelConfig.from_environment()
        conversation = Conversation(ChatClient(config) if config else None)
    store = ExperimentStore(conversation)
    app.extensions['experiments'] = store
    register_pages(app, conversation)
    register_judge_routes(app, store)
    register_respondent_routes(app, store)
    register_errors(app)
    return app


def register_pages(app, conversation):
    @app.get('/')
    def index():
        return render_template('index.html', backend=conversation.backend_label,
                               personas=conversation.library.personas.values())

    @app.get('/respond/<invite>')
    def human_page(invite):
        return render_template('respond.html', invite=invite)


def register_judge_routes(app, store):
    @app.post('/api/sessions')
    def new_session():
        body = request_object()
        identifier, invite = store.create(body.get('persona', 'technical'),
                                          body.get('kind', 'chat'))
        return jsonify({'id': identifier, 'invite': f'/respond/{invite}',
                        'session': store.view(identifier)}), 201

    @app.get('/api/sessions/<identifier>')
    def session_view(identifier):
        return jsonify(store.view(identifier))

    @app.post('/api/sessions/<identifier>/questions')
    def question(identifier):
        return jsonify(store.ask(identifier, request_object().get('question')))

    @app.post('/api/sessions/<identifier>/verdict')
    def verdict(identifier):
        body = request_object()
        return jsonify(store.reveal(identifier, body.get('guess'), body.get('confidence')))

    @app.get('/api/sessions/<identifier>/export')
    def export(identifier):
        response = jsonify(store.view(identifier))
        response.headers['Content-Disposition'] = 'attachment; filename=turing-session.json'
        return response


def register_respondent_routes(app, store):
    @app.get('/api/respond/<invite>')
    def human_view(invite):
        return jsonify(store.human_view(invite))

    @app.post('/api/respond/<invite>')
    def human_answer(invite):
        store.answer_human(invite, request_object().get('answer'))
        return jsonify(store.human_view(invite))


def register_errors(app):
    @app.errorhandler(ValueError)
    def bad_input(exc):
        return jsonify({'error': str(exc)}), 400

    @app.errorhandler(LookupError)
    def missing_session(exc):
        return jsonify({'error': str(exc)}), 404

    @app.errorhandler(ModelError)
    def model_failure(exc):
        return jsonify({'error': str(exc)}), 502

    @app.errorhandler(413)
    def oversized(_exc):
        return jsonify({'error': 'Request is too large'}), 413

    @app.after_request
    def local_headers(response):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        return response


if __name__ == '__main__':
    create_app().run(host='127.0.0.1', port=5001, debug=False)
