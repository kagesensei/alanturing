"""Generate exact-answer domain examples from tested engines, without persona data."""

import argparse
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
for folder in ('turing_machines/basic_simulator', 'turing_machines/arithmetic_turing_machine',
               'cryptanalysis/frequency_analysis'):
    sys.path.insert(0, str(ROOT / folder))

from turing_machine import binary_increment_machine  # pylint: disable=wrong-import-position
from arithmetic_turing_machine import (  # pylint: disable=wrong-import-position
    addition_tape, unary_addition_machine,
)
from frequency_analysis import caesar_encrypt  # pylint: disable=wrong-import-position


SYSTEM = (
    'You are turing-a1, a computational-reasoning and classical-cryptanalysis assistant. '
    'Give a brief explanation and end with ANSWER: followed by the exact requested result. '
    'You are not a historical persona and do not speak as Alan Turing.'
)
PASSAGES = (
    'THE LAMP IS ON THE DESK', 'A TRAIN ARRIVES BEFORE NOON',
    'WE COUNT THE STARS AT NIGHT', 'THE RIVER FLOWS PAST THE MILL',
    'PLEASE CLOSE THE WINDOW', 'BRING A MAP TO THE STATION',
    'THE SMALL BOAT REACHED THE SHORE', 'A LETTER WAITS BESIDE THE DOOR',
    'THE CLOCK STRUCK SEVEN', 'SNOW COVERED THE EMPTY ROAD',
)


def example(family, key, question, explanation, answer, source):
    return {
        'prompt': [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': question}],
        'completion': [{'role': 'assistant', 'content': f'{explanation}\nANSWER: {answer}'}],
        'meta': {'family': family, 'group': f'{family}:{key}', 'answer': str(answer),
                 'source': source, 'generator': 'deterministic engine; no teacher model'},
    }


def generate_examples():
    incrementer = binary_increment_machine()
    for number in range(512):
        bits = format(number, 'b')
        result = incrementer.run(bits)
        yield example('binary_increment', bits, f'Increment the binary integer {bits} by one.',
                      'Add one in base two, carrying through trailing ones.', result.tape,
                      'turing_machines/basic_simulator/turing_machine.py')
    adder = unary_addition_machine()
    for left in range(16):
        for right in range(16):
            result = adder.run(addition_tape(left, right))
            yield example('unary_addition', f'{left}:{right}',
                          f'A unary tape contains {left} ones, +, then {right} ones. '
                          'After addition, give the decimal count of ones.',
                          'Unary addition combines the two groups of ones.', result.value,
                          'turing_machines/arithmetic_turing_machine/arithmetic_turing_machine.py')
    for index, passage in enumerate(PASSAGES):
        for shift in range(1, 26):
            ciphertext = caesar_encrypt(passage, shift)
            yield example('caesar_decryption', index,
                          f'Decrypt Caesar ciphertext {ciphertext!r} with forward shift {shift}.',
                          f'Shift each letter back {shift} places modulo 26; preserve spaces.',
                          passage, 'cryptanalysis/frequency_analysis/frequency_analysis.py')


def partition(examples):
    examples = list(examples)
    splits = {'train': [], 'validation': [], 'test': []}
    assignments = {}
    for family in sorted({row['meta']['family'] for row in examples}):
        groups = {row['meta']['group'] for row in examples if row['meta']['family'] == family}
        ordered = sorted(groups, key=lambda group: hashlib.sha256(group.encode()).hexdigest())
        if len(ordered) < 3:
            raise ValueError('Each task family needs at least three independent groups')
        held_out = max(1, len(ordered) // 10)
        for index, group in enumerate(ordered):
            if index < held_out:
                assignments[group] = 'test'
            elif index < 2 * held_out:
                assignments[group] = 'validation'
            else:
                assignments[group] = 'train'
    for row in examples:
        splits[assignments[row['meta']['group']]].append(row)
    validate_splits(splits)
    return splits


def validate_splits(splits):
    seen_groups = {}
    seen_prompts = {}
    expected_families = {row['meta']['family'] for row in splits['train']}
    for name in ('train', 'validation', 'test'):
        rows = splits[name]
        if not rows:
            raise ValueError(f'{name} is empty')
        if {row['meta']['family'] for row in rows} != expected_families:
            raise ValueError(f'{name} is missing a task family')
        for row in rows:
            group = row['meta']['group']
            prompt = json.dumps(row['prompt'], sort_keys=True)
            if seen_groups.get(group, name) != name or seen_prompts.get(prompt, name) != name:
                raise ValueError('Training/evaluation leakage: group or prompt crosses splits')
            seen_groups[group] = name
            seen_prompts[prompt] = name
            if not row['completion'][0]['content'].endswith('ANSWER: ' + row['meta']['answer']):
                raise ValueError('Completion does not match its verified answer')


def write_dataset(output: Path) -> dict:
    splits = partition(generate_examples())
    output.mkdir(parents=True, exist_ok=True)
    manifest = {'status': 'generated; not model training', 'splits': {}, 'sources': {}}
    for name, rows in splits.items():
        content = ''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows)
        (output / f'{name}.jsonl').write_text(content, encoding='utf-8', newline='\n')
        manifest['splits'][name] = {'examples': len(rows),
                                    'sha256': hashlib.sha256(content.encode()).hexdigest()}
        for row in rows:
            source = row['meta']['source']
            manifest['sources'][source] = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).parent / 'data')
    print(json.dumps(write_dataset(parser.parse_args().output), indent=2))
