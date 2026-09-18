"""Reproducible held-out comparison; evaluation never changes the fitness dictionary."""

import argparse
import json
from pathlib import Path
import platform
import random
import statistics
import time

from genetic_codebreaker import COMMON_WORDS, crack_substitution_cipher
from frequency_analysis import ALPHABET, frequency_substitution_guess


HERE = Path(__file__).resolve().parent


def encrypt_substitution(plaintext: str, seed: int) -> str:
    key = list(ALPHABET)
    random.Random(seed).shuffle(key)
    mapping = dict(zip(ALPHABET, key))
    return ''.join(mapping.get(char, char) for char in plaintext.upper())


def letter_accuracy(expected: str, actual: str) -> float:
    if len(expected) != len(actual):
        raise ValueError('Predicted and reference text must have equal lengths')
    letters = [(left, right) for left, right in zip(expected.upper(), actual.upper())
               if left in ALPHABET]
    if not letters:
        raise ValueError('Reference must contain ASCII letters')
    return sum(left == right for left, right in letters) / len(letters)


def summarize(rows: list[dict]) -> dict:
    summary = {}
    for method in ('frequency', 'genetic'):
        selected = [row for row in rows if row['method'] == method]
        scores = [row['letter_accuracy'] for row in selected]
        summary[method] = {
            'trials': len(selected), 'mean_letter_accuracy': statistics.mean(scores),
            'min_letter_accuracy': min(scores), 'max_letter_accuracy': max(scores),
            'exact_recoveries': sum(row['exact_match'] for row in selected),
            'mean_seconds': statistics.mean(row['seconds'] for row in selected),
        }
    return summary


def run_benchmark(corpus: dict, generations: int = 300) -> dict:
    rows = []
    for case in corpus['cases']:
        plaintext = case['text'].upper()
        for key_seed in (17, 29):
            ciphertext = encrypt_substitution(plaintext, key_seed)
            start = time.perf_counter()
            baseline = frequency_substitution_guess(ciphertext)
            rows.append(measure(case['id'], key_seed, None, 'frequency',
                                plaintext, baseline, time.perf_counter() - start))
            for search_seed in (0, 1, 2):
                start = time.perf_counter()
                result = crack_substitution_cipher(
                    ciphertext, generations=generations, rng=random.Random(search_seed),
                )
                rows.append(measure(case['id'], key_seed, search_seed, 'genetic',
                                    plaintext, result.plaintext, time.perf_counter() - start))
            print(f"Completed {case['id']}, key seed {key_seed}", flush=True)
    return {
        'python': platform.python_version(), 'platform': platform.platform(),
        'corpus_provenance': corpus['provenance'],
        'parameters': {'population_size': 200, 'generations': generations,
                       'mutation_rate': 0.15, 'elite_count': 10, 'tournament_size': 5},
        'dictionary_size': len(COMMON_WORDS), 'trials': rows, 'summary': summarize(rows),
    }


def measure(case, key_seed, search_seed, method, expected, actual, seconds) -> dict:
    return {
        'case': case, 'key_seed': key_seed, 'search_seed': search_seed, 'method': method,
        'letter_accuracy': letter_accuracy(expected, actual),
        'exact_match': expected == actual, 'seconds': seconds, 'recovered_text': actual,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generations', type=int, default=300)
    parser.add_argument('--output', type=Path, default=HERE / 'benchmark_results.json')
    args = parser.parse_args()
    corpus = json.loads((HERE / 'benchmark_corpus.json').read_text(encoding='utf-8'))
    result = run_benchmark(corpus, args.generations)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__':
    main()
