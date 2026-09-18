# turing-a1 training workflow

This directory keeps turing-a1's training code shareable in this Git repository,
separate from the historical persona dataset and from APT_Watch's analyst model.
It is a self-contained workflow directory, not a nested Git repository.

**Current status:** deterministic dataset generation, validation, leakage checks,
configuration, a QLoRA training entry point, endpoint evaluation, and an adapter
server are implemented. Data/contract tests and the dependency-free dry run have
been executed. **GPU training, real model inference, distillation, and publication
have not been executed.** The GPU dependency pins are a proposed compatible
stack; they still need installation and a hardware trial in this environment.

## First model

The default is [Meta Llama 3.2 3B Instruct](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct),
with an output named `Llama-3.2-3B-turing-a1-qlora-v1`. The detected local GPU is
an RTX 2070 with 8 GiB VRAM. Start with 4-bit NF4, FP16 compute, a 256-token
sequence limit, batch size one, rank-eight adapters on attention Q/V projections,
and gradient checkpointing. This is a conservative starting point, not a
measured promise that a full training run fits. BF16 and Flash Attention are
not assumed for this GPU.

`config.json` accepts another compatible Hugging Face checkpoint, including a
full-precision abliterated derivative. Use its actual model ID and preserve the
upstream provenance/license. **Do not use a GGUF file as the training checkpoint.**
Keep an unmodified baseline for comparison. Do not append `abliterated`,
`distilled`, or `claudetuned` unless those steps actually happened and are
documented. This workflow performs supervised fine-tuning with QLoRA; it does
not perform ablation or teacher-model distillation.

The base model may require accepting Meta's access terms and authenticating with
Hugging Face. The Llama license requires derivative model names to begin with
“Llama”; distribution also needs the upstream license/notice and “Built with
Llama” attribution. Review the linked model's terms when preparing publication.

## Generate and inspect data

Activate the root Python 3.12 environment:

```text
python finetune/prepare_data.py
python finetune/train.py --dry-run
python -m unittest discover -s finetune -v
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
python -m pip install -r finetune/requirements.txt
python -m pip check
python -c "import torch; print(torch.cuda.is_available())"
python finetune/train.py --max-steps 5
```

The CUDA wheel and your installed driver must be compatible. Current
[bitsandbytes installation guidance](https://huggingface.co/docs/bitsandbytes/main/en/installation)
describes platform/GPU support. If the local Windows stack fails, use a supported
Linux GPU environment rather than claiming the trial succeeded.

Before a full one-epoch run, choose a new `output_name` so the trial is retained:

```text
python finetune/train.py
```

Training resolves `revision` to a Hub commit SHA and records it in the adapter
configuration and run manifest. Set `revision` to that SHA for a repeat run.
The run manifest also records package versions, dataset hashes, GPU, and measured
training/validation metrics. Completion-only loss avoids learning to reproduce
the prompt. Overlength examples fail rather than silently truncating the answer.
The untouched test split is never supplied to the trainer. Training refuses to
overwrite an existing output directory and never publishes automatically.

The implementation follows [TRL 0.26.2 SFT](https://huggingface.co/docs/trl/v0.26.2/en/sft_trainer)
and [PEFT quantization](https://huggingface.co/docs/peft/en/developer_guides/quantization).
Standard CI covers the lightweight workflow and serving contract. It does not
install GPU dependencies or claim to exercise the training loop.

## Serve and evaluate a trained adapter

After an actual successful training run:

```text
python finetune/serve.py --adapter finetune/outputs/Llama-3.2-3B-turing-a1-qlora-v1
```

The local server reloads the recorded base revision and adapter and exposes
`http://127.0.0.1:8080/v1/chat/completions`. Generation is greedy, bounded to
512 output tokens and 4,096 input tokens. Set `TURING_MODEL_API_KEY` to require
a bearer key. It is a single-process local development server.

Configure the [simulator](../bonus/turing_test_simulator) with this endpoint and
the output model name. Its historical mode requires evidence-selection JSON,
which this starter arithmetic/cipher dataset does **not** train explicitly.
Evaluate that capability separately; invalid persona replies fail closed.

Run `evaluate.py` against the same test split for both the served original base
and the served adapter, changing the model and output filenames:

```text
python finetune/evaluate.py --endpoint http://127.0.0.1:8080/v1/chat/completions --model Llama-3.2-3B-turing-a1-qlora-v1 --output finetune/adapter-evaluation.json
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
[`HUGGINGFACE.md`](../HUGGINGFACE.md) only after publication.

If you add teacher-generated explanations later, log the teacher model/revision,
prompts, parameters, and dataset lineage; verify answers against the engines and
review explanations. Reserve new untouched evaluation data before doing so.
Do not claim teacher distillation just because a generator used templates.

Generated data, weights, checkpoints, and credentials are gitignored. No GPU
packages are installed, no model weights are downloaded, and no paid teacher
calls are made by the preparation/dry-run commands.
