"""Score held-out exact answers from a served base model or trained adapter."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

from training_config import HERE, load_splits


SIMULATOR = HERE.parent / 'bonus' / 'turing_test_simulator'
sys.path.insert(0, str(SIMULATOR))
from model_client import ChatClient, ModelConfig, ModelError  # pylint: disable=wrong-import-position


def score_examples(client, rows: list[dict]) -> dict:
    predictions = []
    for row in rows:
        try:
            response = client.complete(row['prompt'])
            answer = response.rsplit('ANSWER:', 1)[-1].strip() if 'ANSWER:' in response else None
            prediction = {'response': response, 'answer': answer, 'error': None}
        except ModelError as exc:
            prediction = {'response': None, 'answer': None, 'error': str(exc)}
        prediction.update({'group': row['meta']['group'], 'family': row['meta']['family'],
                           'expected': row['meta']['answer'],
                           'correct': prediction['answer'] == row['meta']['answer']})
        predictions.append(prediction)
    families = sorted({row['family'] for row in predictions})
    scores = {}
    for family in families:
        selected = [row for row in predictions if row['family'] == family]
        scores[family] = {'examples': len(selected),
                         'exact_accuracy': sum(row['correct'] for row in selected) / len(selected)}
    return {'by_family': scores, 'predictions': predictions,
            'errors': sum(row['error'] is not None for row in predictions)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--endpoint', required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--data', type=Path, default=HERE / 'data')
    parser.add_argument('--split', choices=('validation', 'test'), default='test')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    config = ModelConfig(args.endpoint, args.model, os.environ.get('TURING_MODEL_API_KEY', ''))
    splits = load_splits(args.data)
    report = score_examples(ChatClient(config), splits[args.split])
    report.update({'model': args.model, 'split': args.split,
                   'data_sha256': hashlib.sha256((args.data / f'{args.split}.jsonl').read_bytes())
                   .hexdigest()})
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report['by_family'], indent=2))
    if report['errors']:
        raise SystemExit('Evaluation contains endpoint failures; see the report')


if __name__ == '__main__':
    main()
