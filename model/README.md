# Local Llama model

This folder contains the Llama training workflow and the optional historical
persona data. The configured base is `meta-llama/Llama-3.2-3B-Instruct`.
No substitute model family is selected.

## Layout

- `base/`: downloaded Llama base weights (ignored by Git).
- `finetune/`: dataset generation, training, evaluation and serving code.
- `finetune/outputs/Llama-3.2-3B-turing-a1-qlora-v1/`: trained adapter and tokenizer.
- `persona/alan_turing/`: evidence-backed historical persona data and validation.

**Current status:** CUDA PyTorch detects the RTX 2070, dependencies are installed,
and the training data is generated. Training has not run: the Llama repository
returned HTTP 401 and there is no cached Hugging Face login. No trained weights
are claimed to exist.

## Train

Activate the root Python 3.12 environment. Obtain access to the configured
[Llama checkpoint](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct),
then authenticate locally with `hf auth login`. Do not put tokens in source files.

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
