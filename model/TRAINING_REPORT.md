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

Real inference through the chat application's Flask API succeeded: incrementing
`1011` in a full training-style prompt returned `ANSWER: 1100`. A shorter
paraphrase of the same task returned the incorrect `10111`, showing that this
smoke check does not establish reliable exact answers. The full
base-versus-adapter test-set comparison was stopped after the slow base-model
pass reached 57 of 101 prompts. No held-out accuracy is claimed, and the test
split was not included in training.
This small synthetic benchmark measures only binary increment, unary addition,
and Caesar decryption. It does not establish general reasoning or historical
fidelity.
