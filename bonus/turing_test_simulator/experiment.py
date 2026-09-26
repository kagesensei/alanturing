"""Bounded local sessions for chat and a human-versus-machine comparison."""

from dataclasses import dataclass, field
import secrets
import threading
import time

from tools.app_logging import record_chat_event


@dataclass
class Experiment:
    persona: str
    kind: str
    machine_label: str
    invite: str
    rounds: list = field(default_factory=list)
    verdict: dict | None = None
    created: float = field(default_factory=time.monotonic)


def require_text(value, limit=2000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f'Text must contain 1–{limit} characters')
    return value.strip()


class ExperimentStore:
    def __init__(self, conversation):
        self.conversation = conversation
        self.games = {}
        self.lock = threading.RLock()

    def create(self, persona, kind):
        if not isinstance(persona, str) or not isinstance(kind, str):
            raise ValueError('Persona and experiment kind must be strings')
        if persona != 'technical' and persona not in self.conversation.library.personas:
            raise ValueError('Unknown persona')
        if kind not in ('chat', 'blind'):
            raise ValueError('Unknown experiment kind')
        with self.lock:
            expired = [key for key, game in self.games.items()
                       if time.monotonic() - game.created > 7200]
            for key in expired:
                del self.games[key]
            if len(self.games) >= 64:
                raise ValueError('Session capacity reached; restart the app or wait for expiry')
            identifier = secrets.token_urlsafe(24)
            game = Experiment(persona, kind, secrets.choice(('A', 'B')), secrets.token_urlsafe(24))
            self.games[identifier] = game
            persona_options = ({'persona_id': persona, 'label': 'Technical assistant'}
                               if persona == 'technical'
                               else self.conversation.library.personas[persona])
            record_chat_event(identifier, 'chat.started',
                              selected_options={'persona': persona,
                                                'persona_label': persona_options.get('label'),
                                                'period': persona_options.get('period_description'),
                                                'knowledge_cutoff_year': persona_options.get(
                                                    'knowledge_cutoff_year'),
                                                'kind': kind},
                              backend=self.conversation.backend_label)
            return identifier, game.invite

    def get(self, identifier):
        game = self.games.get(identifier)
        if game is None or time.monotonic() - game.created > 7200:
            raise LookupError('Session not found or expired')
        return game

    def ask(self, identifier, question):
        question = require_text(question)
        with self.lock:
            game = self.get(identifier)
            if game.verdict or len(game.rounds) >= 6:
                raise ValueError('This session is complete; start another')
            if game.rounds and game.kind == 'blind' and game.rounds[-1]['human'] is None:
                raise ValueError('Wait for the human respondent before asking another question')
            history = []
            for previous in game.rounds:
                history.extend([{'role': 'user', 'content': previous['question']},
                                {'role': 'assistant', 'content': previous['machine']['text']}])
            answer = self.conversation.answer(question, game.persona, history)
            game.rounds.append({'question': question, 'machine': answer, 'human': None})
            record_chat_event(identifier, 'chat.turn', question=question,
                              response=answer.get('text'),
                              response_label=answer.get('label'),
                              persona=game.persona, kind=game.kind,
                              claim_ids=[claim.get('claim_id') for claim in
                                         answer.get('claims', [])],
                              source_ids=[source.get('source_id') for source in
                                          answer.get('sources', [])])
            return self.view(identifier)

    def view(self, identifier):
        with self.lock:
            game = self.get(identifier)
            rows = []
            for entry in game.rounds:
                row = {'question': entry['question'], 'pending': False}
                if game.kind == 'chat' or game.verdict:
                    row['machine'] = entry['machine']
                    row['human'] = entry['human']
                elif entry['human'] is None:
                    row['pending'] = True
                else:
                    row[game.machine_label] = entry['machine']['text']
                    row['B' if game.machine_label == 'A' else 'A'] = entry['human']
                rows.append(row)
            return {'kind': game.kind, 'persona': game.persona, 'rounds': rows,
                    'verdict': game.verdict, 'backend': self.conversation.backend_label}

    def respondent(self, invite):
        for identifier, game in self.games.items():
            if secrets.compare_digest(game.invite, invite):
                return identifier, self.get(identifier)
        raise LookupError('Invitation not found or expired')

    def human_view(self, invite):
        with self.lock:
            _, game = self.respondent(invite)
            return {'persona': game.persona, 'complete': bool(game.verdict),
                    'rounds': [{'question': row['question'], 'answer': row['human']}
                               for row in game.rounds]}

    def answer_human(self, invite, text):
        text = require_text(text, 8000)
        with self.lock:
            identifier, game = self.respondent(invite)
            if (game.kind != 'blind' or game.verdict or not game.rounds
                    or game.rounds[-1]['human'] is not None):
                raise ValueError('There is no question awaiting a human answer')
            game.rounds[-1]['human'] = text
            record_chat_event(identifier, 'human.response', answer=text,
                              persona=game.persona, kind=game.kind)

    def reveal(self, identifier, guess, confidence):
        valid_confidence = isinstance(confidence, int) and not isinstance(confidence, bool)
        if guess not in ('A', 'B') or not valid_confidence or not 0 <= confidence <= 100:
            raise ValueError('Choose A or B and confidence from 0 to 100')
        with self.lock:
            game = self.get(identifier)
            if game.kind != 'blind' or not game.rounds or game.rounds[-1]['human'] is None:
                raise ValueError('Complete at least one human/model round before judging')
            if game.verdict:
                raise ValueError('The verdict is already recorded')
            game.verdict = {'guess': guess, 'confidence': confidence,
                            'machine_label': game.machine_label,
                            'correct': guess == game.machine_label,
                            'note': 'A local subjective exercise, not evidence of consciousness.'}
            record_chat_event(identifier, 'judge.verdict', guess=guess,
                              confidence=confidence, result=game.verdict)
            return self.view(identifier)
