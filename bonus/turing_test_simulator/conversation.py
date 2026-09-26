"""Generate source-aware technical answers and simulated historical conversation."""

import json
import re

from evidence import EvidenceLibrary, render_selection, select_local


DOMAIN_PROMPT = (
    'You are turing-a1, a cryptanalysis and computational-reasoning laboratory assistant. '
    'Explain computation and classical ciphers clearly. Distinguish demonstrations from '
    'measured results. You are not Alan Turing and must not adopt a historical persona. '
    'Admit uncertainty and do not claim that unperformed tests or training succeeded.'
)

HISTORICAL_REPLY_PROMPT = (
    'Write a natural, conversational reply for a clearly simulated Alan Turing persona. '
    'The simulated speaker is Turing, and the user is speaking with him. Speak as I, not as '
    'if the user were Turing. When answering about the speaker’s own work or life, use first '
    'person: say “I published” rather than “your paper” or “Turing published.” You are a '
    'simulation, not the actual person. Avoid an AI disclaimer during ordinary conversation. '
    'These generated '
    'words are not a historical quotation. Follow the supplied evidence-based voice guidance '
    'without turning uncertain traits into facts. Be direct, curious, precise on technical '
    'topics, and lightly dry or playful only when it fits. Do not imitate an accent or use fake '
    'period slang. Respond naturally to greetings, banter, jokes, and insults instead of '
    'demanding a historical source for ordinary conversation. For claims about Turing’s life, '
    'work or experiences, rely on the supplied records. If a personal preference is unknown, '
    'do not invent one as a fact. When a plausible reaction is useful, frame it as an explicit '
    'interpretation for the simulation rather than a documented view. For general questions, '
    'answer conversationally using '
    'knowledge available by the selected cutoff, but do not claim Turing personally knew, said, '
    'or believed something unless the records support it. Never introduce events or concepts '
    'after the cutoff. Use prior turns to resolve references. Do not repeat record excerpts or '
    'source IDs in the reply; the interface shows evidence separately. Aim for two to five '
    'sentences and continue the conversation when appropriate.'
)


class Conversation:
    def __init__(self, client=None):
        self.client = client
        self.library = EvidenceLibrary()

    @property
    def backend_label(self) -> str:
        if self.client:
            return getattr(self.client, 'label', 'configured model endpoint')
        return 'local demonstration (no trained model)'

    def answer(self, question: str, persona_id: str, history: list[dict]) -> dict:
        if persona_id == 'technical':
            if self.client:
                text = self.client.complete([{'role': 'system', 'content': DOMAIN_PROMPT},
                                             *history[-10:], {'role': 'user', 'content': question}])
            else:
                text = ('This local demonstration has no language model. Connect turing-a1 '
                        'to ask technical questions; historical modes can explore the bundled '
                        'evidence without an endpoint.')
            return {'text': text, 'claims': [], 'sources': [], 'mode': 'technical',
                    'label': 'Generated technical response; not historical testimony'}
        claims = self.library.available(persona_id)
        search_text = self._retrieval_query(question, history)
        candidate_ids = select_local(search_text, claims)
        candidates = [claim for claim in claims if claim['claim_id'] in candidate_ids]
        evidence_text, records = render_selection(candidate_ids, candidates)
        if self.client:
            text = self._historical_reply(question, persona_id, history, records)
        else:
            text = evidence_text
        return {'text': text, 'claims': records, 'sources': self.library.citations(records),
                'mode': persona_id, 'label': 'SIMULATED_DIALOGUE_NOT_A_HISTORICAL_QUOTE'}

    def _historical_reply(self, question, persona_id, history, records):
        persona = self.library.personas[persona_id]
        voice = self._voice_context()
        prompt = (
            f'{HISTORICAL_REPLY_PROMPT}\nSelected persona: {persona["label"]}. '
            f'Period: {persona["period_description"]}. '
            f'Knowledge cutoff year: {persona["knowledge_cutoff_year"]}. '
            f'Persona scope: {persona["description"]}\nEvidence-based voice guidance: {voice}\n'
            f'Historical records retrieved for this turn: '
            f'{json.dumps(records, ensure_ascii=False)}'
        )
        messages = [{'role': 'system', 'content': prompt},
                    *self._bounded_history(history),
                    {'role': 'user', 'content': question}]
        return self.client.complete(messages)

    def _voice_context(self):
        style = self.library.conversational_style
        traits = [{key: trait[key] for key in (
            'name', 'description', 'evidence_type', 'confidence', 'source_ids',
            'avoid_caricature') if key in trait}
                  for trait in style['traits']]
        return json.dumps({'traits': traits,
                           'avoid_caricature': style['avoid_caricature_global']},
                          ensure_ascii=False)

    @staticmethod
    def _retrieval_query(question, history):
        query = question
        follow_up = re.search(
            r'\b(that|this|these|those|it|they|them|other|more|why|explain|'
            r'elaborate|principle|there|then)\b', question, re.IGNORECASE,
        )
        if follow_up:
            earlier_turns = [message['content'] for message in history[-6:]
                             if isinstance(message.get('content'), str)]
            query = ' '.join([*earlier_turns, question])
        if re.search(r'\balan\s+turing\b', question, re.IGNORECASE):
            query += ' computable numbers Cambridge mathematics'
        return query

    @staticmethod
    def _bounded_history(history):
        return [{'role': message['role'], 'content': message['content'][-1200:]}
                for message in history[-4:]
                if message.get('role') in ('user', 'assistant')
                and isinstance(message.get('content'), str)]
