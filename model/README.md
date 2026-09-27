# Local Ministral model

This folder contains the Ministral training workflow and the optional historical
persona data. The configured base is `mistralai/Ministral-3-3B-Instruct-2512-BF16`.
No substitute model family is selected.

## Layout

- `base/`: downloaded Ministral base weights (ignored by Git).
- `finetune/`: dataset generation, training, evaluation and serving code.
- `finetune/outputs/Ministral-3-3B-turing-a1-qlora-v1/`: trained adapter and tokenizer.
- `persona/alan_turing/`: evidence-backed historical persona data and validation.

**Current status:** the GPU trial and full training passed. Real chat inference
returned the expected answer. The full held-out comparison was stopped before
scoring completed.
See [the training report](TRAINING_REPORT.md) for final measurements.

## Hugging Face

The public [turing-a1 Ministral adapter](https://huggingface.co/kageskull/Ministral-3-3B-turing-a1-qlora-v1)
contains the LoRA weights, adapter configuration, tokenizer files and model
card. It does not include the Ministral base-model weights. Download the base
checkpoint separately as described in [the fine-tuning workflow](finetune/README.md).

The public [synthetic computational-task dataset](https://huggingface.co/datasets/kageskull/turing-a1-synthetic-computational-tasks)
contains 1,018 examples split into 816 training, 101 validation and 101 test
examples. It covers binary increment, unary addition and Caesar decryption
with a known shift. The dataset is licensed under GPL-3.0. The historical
persona files are not included in either publication.

## Train

Activate the root Python 3.12 environment. The official checkpoint is public.
The pinned revision and downloaded base weights allow this run to work offline.
See [training setup](finetune/README.md) for dependencies on a new machine.

```powershell
.\.venv\Scripts\Activate.ps1
python model/finetune/prepare_data.py
python model/finetune/train.py
python app.py
```

Open http://127.0.0.1:5000 and follow **Open chat**. Chat loads the completed
local adapter on its first question. No separate inference server is required.
`python bonus/turing_test_simulator/app.py` also runs chat directly on port 5001.
Missing weights produce an explicit error instead of simulated model answers.

Set `TURING_MODEL_ADAPTER` to another completed adapter directory if needed.
An explicitly configured `TURING_MODEL_ENDPOINT` takes precedence over local
loading. Base weights are loaded offline from `base/` when serving.

The starter dataset covers binary increment, unary addition and Caesar decryption.
It does not establish broad reasoning quality or train historical persona claims.
See [the workflow documentation](finetune/README.md) for evaluation and provenance.
