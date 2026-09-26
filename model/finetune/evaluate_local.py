"""Compare base and adapter on the same held-out prompts using offline local weights."""

import argparse
import hashlib
import json
from pathlib import Path

from evaluate import score_examples
from model_runtime import load_text_model
from serve import InferenceEngine
from training_config import HERE, load_splits


class LocalEvaluationClient:
    def __init__(self, engine):
        self.engine = engine
        self.count = 0

    def complete(self, messages):
        result = self.engine.complete(messages, 128)
        self.count += 1
        if not self.count % 10:
            print(f'Evaluated {self.count} prompts', flush=True)
        return result


def write_report(engine, rows, name, manifest, directory):
    report = score_examples(LocalEvaluationClient(engine), rows)
    report.update({'model': name, 'base_model': manifest['base_model'],
                   'revision': manifest['resolved_revision'], 'split': 'test',
                   'max_new_tokens': 128, 'do_sample': False,
                   'data_sha256': hashlib.sha256((HERE / 'data' / 'test.jsonl').read_bytes())
                   .hexdigest()})
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f'{name}.json'
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'model': name, 'by_family': report['by_family'],
                      'errors': report['errors']}, indent=2), flush=True)


def evaluate(directory):
    # pylint: disable=import-outside-toplevel,import-error
    from peft import PeftModel
    from transformers import AutoTokenizer
    # pylint: enable=import-outside-toplevel,import-error

    manifest = json.loads((directory / 'run_manifest.json').read_text(encoding='utf-8'))
    if manifest['status'] != 'adapter trained; not published':
        raise ValueError('Expected a completed adapter')
    rows = load_splits(HERE / 'data')['test']
    base = load_text_model(manifest['base_model'], manifest['resolved_revision'], offline=True)
    base.eval()
    tokenizer = AutoTokenizer.from_pretrained(directory, local_files_only=True)
    reports = HERE / 'evaluations' / manifest['output_name']
    write_report(InferenceEngine(base, tokenizer), rows, 'baseline', manifest, reports)
    adapted = PeftModel.from_pretrained(base, directory)
    adapted.eval()
    write_report(InferenceEngine(adapted, tokenizer), rows, 'adapter', manifest, reports)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adapter', type=Path, required=True)
    evaluate(parser.parse_args().adapter)
