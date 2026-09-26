# Ministral fine-tuning report

The original one-epoch Ministral 3 3B Instruct QLoRA run completed locally on
the RTX 2070. The checkpoint is Apache-2.0 licensed. The model's multimodal
checkpoint was reduced to its verified language weights; the vision components
were outside the text-only scope.

- Base revision: `b6d637bef2393152b3da2b2fde72eecdee30557e`
- Training data: 816 deterministic examples; validation: 101; held-out test: 101
- Configuration: 4-bit NF4, rank 8, 16-step gradient accumulation, 256-token cap
- Training loss: 0.381; validation loss: 0.294
- Peak allocated GPU memory: 5,008,672,768 bytes (about 4.67 GiB)
- Training duration: 463.7 seconds

Base and fine-tuned exact-answer test metrics will be added after the local
held-out evaluation completes. The test split is not included in training.
This small synthetic benchmark measures only binary increment, unary addition,
and Caesar decryption. It does not establish general reasoning or historical
fidelity.
