"""Conservative, extractive access to the existing persona source of truth."""

import json
from pathlib import Path
import re
import sys


PERSONA_DIR = Path(__file__).resolve().parents[2] / 'persona' / 'alan_turing'
if str(PERSONA_DIR) not in sys.path:
    sys.path.insert(0, str(PERSONA_DIR))

from persona_validation import (  # pylint: disable=wrong-import-position
    Confidence, EvidenceType, classify_claim, validate_all,
)


def load_document(name: str) -> dict:
    return json.loads((PERSONA_DIR / name).read_text(encoding='utf-8'))


class EvidenceLibrary:
    def __init__(self):
        issues = validate_all()
        if issues:
            raise ValueError(f'Persona data failed validation: {issues}')
        self.personas = {row['persona_id']: row
                         for row in load_document('persona.json')['temporal_personas']}
        self.sources = {row['source_id']: row for row in load_document('sources.json')['sources']}
        self.events = load_document('chronology.json')['events']
        self.interests = load_document('interests.json')['interests']

    def available(self, persona_id: str) -> list[dict]:
        if persona_id not in self.personas:
            raise ValueError('Unknown persona')
        persona = self.personas[persona_id]
        cutoff = persona['knowledge_cutoff_year']
        claims = []
        for event in self.events:
            if cutoff is not None:
                # Exclude whole records spanning later years rather than silently
                # rewriting historical evidence to fit the requested persona.
                dates = re.findall(r'\b(?:18|19|20)\d{2}\b',
                                   event['date_display'] + ' ' + event['description'])
                if (event['event_id'] not in persona['known_events'] or event['year'] > cutoff
                        or any(int(year) > cutoff for year in dates)):
                    continue
            claims.append(self._claim(event, event['event_id'], event['description']))
        for interest in self.interests:
            if interest['evidence_type'] == 'UNKNOWN':
                text = (f"The supplied evidence does not establish "
                        f"{interest['category']} preferences.")
                claims.append(self._claim(interest, interest['interest_id'], text))
            elif persona['is_fictional']:
                # Undated biography is available only outside historical cutoff modes.
                claims.append(self._claim(interest, interest['interest_id'], interest['claim']))
        return claims

    def _claim(self, record: dict, claim_id: str, text: str) -> dict:
        category = classify_claim(EvidenceType(record['evidence_type']),
                                  Confidence(record['confidence'])).value
        return {
            'claim_id': claim_id, 'text': text, 'evidence_type': record['evidence_type'],
            'confidence': record['confidence'], 'claim_category': category,
            'source_ids': record['source_ids'],
        }

    def citations(self, claims: list[dict]) -> list[dict]:
        identifiers = sorted({source for claim in claims for source in claim['source_ids']})
        return [self.sources[identifier] for identifier in identifiers]


def select_local(question: str, claims: list[dict]) -> list[str]:
    """Small lexical demo, explicitly not a trained conversational model."""
    words = set(re.findall(r'[a-z]{4,}', question.lower())) - {
        'what', 'when', 'where', 'which', 'your', 'about', 'tell', 'turing', 'have',
    }
    scored = [(len(words & set(re.findall(r'[a-z]{4,}', claim['text'].lower()))), claim)
              for claim in claims]
    return [claim['claim_id'] for score, claim in sorted(scored, key=lambda row: -row[0])[:3]
            if score]


def render_selection(selected: list[str], claims: list[dict]) -> tuple[str, list[dict]]:
    lookup = {claim['claim_id']: claim for claim in claims}
    if (not isinstance(selected, list) or len(selected) > 3
            or any(not isinstance(value, str) or value not in lookup for value in selected)):
        raise ValueError('Model selected unavailable evidence')
    records = [lookup[value] for value in dict.fromkeys(selected)]
    if not records:
        return 'The supplied evidence within this persona scope does not establish an answer.', []
    lines = ['Record excerpts related to your question (not historical quotations):']
    for record in records:
        sources = ', '.join(record['source_ids']) or 'no supporting source'
        lines.append(f"[{record['claim_id']}; {record['evidence_type']}; "
                     f"{record['confidence']}; {sources}] {record['text']}")
    return '\n\n'.join(lines), records
