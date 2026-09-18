"""Validate training inputs without importing or downloading GPU libraries."""

import hashlib
from importlib import metadata
import json
from pathlib import Path

from prepare_data import validate_splits


HERE = Path(__file__).resolve().parent


def load_config(path: Path) -> dict:
    config = json.loads(path.read_text(encoding='utf-8'))
    for key in ('base_model', 'revision', 'output_name'):
        if not isinstance(config.get(key), str) or not config[key].strip():
            raise ValueError(f'{key} must be a non-empty string')
    for key in ('max_length', 'lora_rank', 'gradient_accumulation_steps', 'seed'):
        value = config.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f'{key} must be a positive integer')
    if config['max_length'] > 2048 or config['lora_rank'] > 64:
        raise ValueError('Configuration exceeds this small-model workflow scope')
    if any(token in config['output_name'] for token in ('/', '\\', '..')):
        raise ValueError('output_name must be a simple directory name')
    return config


def load_splits(directory: Path) -> dict:
    splits = {}
    for name in ('train', 'validation', 'test'):
        with (directory / f'{name}.jsonl').open(encoding='utf-8') as stream:
            splits[name] = [json.loads(line) for line in stream if line.strip()]
    validate_splits(splits)
    return splits


def preflight(config: dict, directory: Path) -> dict:
    splits = load_splits(directory)
    versions = {}
    packages = ('torch', 'transformers', 'trl', 'peft', 'datasets', 'accelerate', 'bitsandbytes')
    for package in packages:
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = None
    return {'base_model': config['base_model'], 'output_name': config['output_name'],
            'versions': versions, 'counts': {name: len(rows) for name, rows in splits.items()},
            'dataset_hashes': {name: hashlib.sha256((directory / f'{name}.jsonl').read_bytes())
                               .hexdigest() for name in splits},
            'status': 'inputs checked; no GPU training executed'}
