# turing-a1 training workflow

This directory keeps turing-a1's training code shareable in this Git repository,
separate from the historical persona dataset and from APT_Watch's analyst model.
It is a self-contained workflow directory, not a nested Git repository.

**Current status:** a two-step GPU trial and the full one-epoch run completed
on the RTX 2070. Real Flask chat inference returned the expected result. The
full held-out comparison was stopped before scoring completed; see
[the model report](../TRAINING_REPORT.md).

## Base model and local hardware

The approved base is
[Ministral 3 3B Instruct BF16](https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512-BF16),
pinned to commit `b6d637bef2393152b3da2b2fde72eecdee30557e`. The output is
`Ministral-3-3B-turing-a1-qlora-v1`. This is a text-only QLoRA adaptation of
Mistral's language weights. The vision tower and projector are not loaded.
Missing or unmapped language weights abort loading rather than silently training
randomly initialized parameters. Base files are stored in `model/base/`.

The RTX 2070 has 8 GiB VRAM. The run uses 4-bit NF4, FP16 compute, a 256-token
sequence limit, batch size one, rank-eight adapters on attention Q/V projections,
gradient accumulation of 16, and gradient checkpointing. Trainable adapter
parameters use FP32 for compatibility with FP16 gradient scaling.

Transformers 5.3.0 supports the Ministral architecture. We use its `Trainer`
with PEFT and explicit completion-only labels. Prompt and padding tokens have
label `-100`; the complete answer and EOS remain supervised. Every example's
prompt prefix and length are validated before training. The old TRL trainer is
not used because its tokenization contract differs from Transformers 5.

The base is Apache-2.0 licensed. This workflow performs supervised QLoRA; it
has not performed ablation or teacher distillation. Historical persona evidence
remains a separate, optional application layer.

## Generate and inspect data

Activate the root Python 3.12 environment:

```text
python model/finetune/prepare_data.py
python model/finetune/train.py --dry-run
python -m unittest discover -s model/finetune -v
```

The generator creates **1,018** exact-answer examples from tested engines:
binary increment, unary addition, and Caesar decryption with a known shift.
Outputs are **816 training, 101 validation, 101 test** examples. Groups are split
deterministically within each task family; all Caesar shifts of one plaintext
stay together. Every task family appears in every split. Cross-split duplicate
prompts/groups and incorrect answer suffixes are rejected. Source-file and
dataset hashes are recorded in `data/manifest.json`.

These are deliberately narrow starter tasks, not evidence that the resulting
model is a broadly capable cryptanalyst. No personality profiles, speculative
preferences, or fabricated quotations enter domain training. They also are not
the genetic-codebreaker benchmark corpus. Review generated examples before
training; use a separate development dataset to expand the domain.

## Install the training stack and run a small trial

Install the [CUDA-enabled PyTorch 2.8 wheel](https://pytorch.org/get-started/previous-versions/)
in the activated root environment, followed by the project pins:

```text
python -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cu126
python -m pip install -r model/finetune/requirements.txt
python -m pip check
python -c "import torch; print(torch.cuda.is_available())"
python model/finetune/train.py --config model/finetune/trial_config.json --max-steps 2
```

The CUDA wheel and your installed driver must be compatible. Current
[bitsandbytes installation guidance](https://huggingface.co/docs/bitsandbytes/main/en/installation)
describes platform/GPU support. If the local Windows stack fails, use a supported
Linux GPU environment rather than claiming the trial succeeded.

The trial configuration has a separate output name. Start the full one-epoch run with:

```text
python model/finetune/train.py
```

Training resolves `revision` to a Hub commit SHA and records it in the adapter
configuration and run manifest. Set `revision` to that SHA for a repeat run.
The run manifest also records package versions, dataset hashes, GPU, and measured
training/validation metrics. Completion-only loss avoids learning to reproduce
the prompt. Overlength examples fail rather than silently truncating the answer.
The untouched test split is never supplied to the trainer. Training refuses to
overwrite an existing output directory and never publishes automatically.

The implementation uses [Transformers Trainer](https://huggingface.co/docs/transformers/main_classes/trainer)
and [PEFT quantization](https://huggingface.co/docs/peft/en/developer_guides/quantization).
Standard CI covers the lightweight workflow and serving contract. It does not
install GPU dependencies or claim to exercise the training loop.

## Serve and evaluate a trained adapter

After an actual successful training run:

```text
python model/finetune/serve.py --adapter model/finetune/outputs/Ministral-3-3B-turing-a1-qlora-v1
```

The local server reloads the recorded base revision and adapter and exposes
`http://127.0.0.1:8080/v1/chat/completions`. Generation is greedy, bounded to
512 output tokens and 4,096 input tokens. Set `TURING_MODEL_API_KEY` to require
a bearer key. It is a single-process local development server.

The [simulator](../../bonus/turing_test_simulator) loads the local adapter directly
by default. This separate endpoint is optional. Its historical mode requires evidence-selection JSON,
which this starter arithmetic/cipher dataset does **not** train explicitly.
Evaluate that capability separately; invalid persona replies fail closed.

Run the offline base-versus-adapter comparison with identical greedy decoding:

```text
python model/finetune/evaluate_local.py --adapter model/finetune/outputs/Ministral-3-3B-turing-a1-qlora-v1
```

JSON predictions and metrics are saved under `model/finetune/evaluations/`.
Alternatively, run `evaluate.py` against the same test split for both the served original base
and the served adapter, changing the model and output filenames:

```text
python model/finetune/evaluate.py --endpoint http://127.0.0.1:8080/v1/chat/completions --model Ministral-3-3B-turing-a1-qlora-v1 --output model/finetune/adapter-evaluation.json
```

Reports include predictions, exact-answer accuracy by task, endpoint failures,
and the dataset hash. Baseline and adapter must use the same prompts, decoding
settings, and test hash. Missing `ANSWER:` or incorrect answers fail the metric;
generation errors remain in the denominator. These small exact-answer tasks do
not measure explanation quality, broad reasoning, or historical fidelity.

## Share the result

Publishing a LoRA adapter with an honest model card is a valid first release;
merging and GGUF conversion can follow after measured evaluation. Use
`MODEL_CARD_TEMPLATE.md` as a starting point, fill it from `run_manifest.json`
and base/adapter evaluations, and include upstream license/attribution files.
Upload the **trained adapter output**, not this untrained configuration, under
`kageskull/<actual-model-name>`. Record the actual published link in
[`HUGGINGFACE.md`](../../HUGGINGFACE.md) only after publication.

If you add teacher-generated explanations later, log the teacher model/revision,
prompts, parameters, and dataset lineage; verify answers against the engines and
review explanations. Reserve new untouched evaluation data before doing so.
Do not claim teacher distillation just because a generator used templates.

Generated data, weights, checkpoints, and credentials are gitignored. No GPU
packages are installed, no model weights are downloaded, and no paid teacher
calls are made by the preparation/dry-run commands.
