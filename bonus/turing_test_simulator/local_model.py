"""Lazy local adapter loading shared by standalone chat and the project launcher."""

import os
from pathlib import Path
import sys
import threading

from model_client import ModelError


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


class LocalModelClient:
    def __init__(self, directory=None):
        self.directory = Path(directory or os.environ.get(
            'TURING_MODEL_ADAPTER',
            ROOT / 'model' / 'finetune' / 'outputs' / 'Ministral-3-3B-turing-a1-qlora-v1',
        ))
        self.engine = None
        self.lock = threading.Lock()

    @property
    def label(self):
        if not (self.directory / 'run_manifest.json').is_file():
            return 'local Ministral adapter missing; training required'
        return f'local fine-tuned model: {self.directory.name}'

    def complete(self, messages):
        with self.lock:
            try:
                if self.engine is None:
                    if not (self.directory / 'run_manifest.json').is_file():
                        raise ModelError('Model missing. Run model/finetune/train.py first.')
                    # Keep GPU libraries optional until the first actual model request.
                    from model.finetune.serve import load_adapter  # pylint: disable=import-outside-toplevel

                    self.engine, _name = load_adapter(self.directory)
                return self.engine.complete(messages, 256)
            except (ImportError, OSError, ValueError, RuntimeError) as exc:
                raise ModelError(f'Local model could not respond: {exc}') from exc
