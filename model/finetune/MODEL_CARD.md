---
base_model:
- mistralai/Ministral-3-3B-Instruct-2512-BF16
library_name: peft
pipeline_tag: text-generation
license: apache-2.0
tags:
- lora
- education
- cryptanalysis
- computational-reasoning
---

# turing-a1 Ministral 3 3B QLoRA adapter

This repository contains the LoRA adapter and tokenizer files for turing-a1. It
does not contain the foundation model weights. It was fine-tuned from
[Mistral AI's Ministral 3 3B Instruct BF16](https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512-BF16),
revision `b6d637bef2393152b3da2b2fde72eecdee30557e`. The upstream model is
licensed under Apache 2.0. Review the upstream model card and license before
use.

## Intended use

This is an educational experiment in narrow computational tasks. Training
examples cover binary increment, unary addition and Caesar decryption with a
known shift. It is not a general cybersecurity model, a cryptographic tool for
protecting information, or a source of reliable historical claims. The
historical Turing persona in the associated application is a separate,
evidence-based layer and was not used as fine-tuning data.

## Training

The fine-tuning run used synthetic, deterministic examples generated from tested
project implementations. The manifest records 816 training examples, 101
validation examples and 101 held-out test examples. Training used one epoch,
4-bit NF4 QLoRA, rank 8, alpha 16, attention `q_proj` and `v_proj`, a 256-token
sequence limit and gradient accumulation of 16 on an NVIDIA RTX 2070. The model
was trained as a text-only adapter; vision components were not loaded.

Recorded training loss was 0.381 and validation loss was 0.294. These losses do
not establish task accuracy. The complete held-out base-versus-adapter
comparison was stopped after 57 of 101 base-model prompts. No held-out accuracy
is claimed. A full-format binary increment smoke test succeeded, while a shorter
paraphrase of the same task failed. These results show that the adapter can be
inconsistent even on its narrow training domain.

The dataset was split by task groups to avoid related examples crossing splits.
The held-out test split was not used during training. Training scripts and
reproducibility details are in the linked project repository.

## Limitations and risks

The adapter has limited training coverage and incomplete held-out evaluation.
It may give incorrect answers, including on tasks similar to training examples.
Do not rely on it for security decisions, operational cryptanalysis, or
high-impact decisions. Verify outputs independently and do not provide secrets
or sensitive data to a chat application.

## Load the adapter

Use a compatible Transformers and PEFT installation, the exact base revision
listed above, and hardware that can load the base model. For example:

```python
from peft import PeftModel
from transformers import AutoConfig, AutoModelForCausalLM

base_id = "mistralai/Ministral-3-3B-Instruct-2512-BF16"
revision = "b6d637bef2393152b3da2b2fde72eecdee30557e"
config = AutoConfig.from_pretrained(base_id, revision=revision)
load_options = {}
if config.model_type == "mistral3":
    config = config.text_config
    load_options["key_mapping"] = {r"^language_model\.": ""}
base = AutoModelForCausalLM.from_pretrained(
    base_id, revision=revision, config=config, **load_options
)
model = PeftModel.from_pretrained(
    base, "kageskull/Ministral-3-3B-turing-a1-qlora-v1"
)
```

This example uses the unquantized base. Follow the upstream license and model
instructions for the base checkpoint and adapt loading to the available GPU.

## Citation and attribution

Base model: [Mistral AI, Ministral 3 3B Instruct 2512 BF16](https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512-BF16).
Upstream license: [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
Training code and report: [Alan Turing: A Tribute in Code](https://github.com/kagesensei/alanturing/tree/main/model/finetune).
