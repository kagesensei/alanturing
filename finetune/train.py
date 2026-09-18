"""Train a small QLoRA adapter; --dry-run validates inputs without GPU dependencies."""

import argparse
import json
from pathlib import Path

from training_config import HERE, load_config, load_splits, preflight


def load_model(config: dict, splits: dict):
    # Optional GPU dependencies are loaded only for an actual training run.
    # The stdlib data-validation suite intentionally does not require this stack.
    # pylint: disable=import-outside-toplevel,import-error
    import torch
    from huggingface_hub import model_info
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, set_seed
    # pylint: enable=import-outside-toplevel,import-error

    if not torch.cuda.is_available():
        raise ValueError('CUDA-enabled PyTorch and a compatible GPU are required')
    set_seed(config['seed'])
    revision = model_info(config['base_model'], revision=config['revision']).sha
    tokenizer = AutoTokenizer.from_pretrained(config['base_model'], revision=revision)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = 'right'
    ensure_lengths(tokenizer, splits, config['max_length'])
    quantization = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                                     bnb_4bit_use_double_quant=True,
                                     bnb_4bit_compute_dtype=torch.float16)
    model = AutoModelForCausalLM.from_pretrained(
        config['base_model'], revision=revision, quantization_config=quantization,
        device_map={'': 0}, torch_dtype=torch.float16, attn_implementation='sdpa',
    )
    model.config.use_cache = False
    return model, tokenizer, revision


def build_datasets(splits):
    from datasets import Dataset  # pylint: disable=import-outside-toplevel,import-error

    return {name: Dataset.from_list([{'prompt': row['prompt'], 'completion': row['completion']}
                                    for row in splits[name]]) for name in ('train', 'validation')}


def build_trainer(config, output, model, tokenizer, splits, max_steps, revision):
    # pylint: disable=import-outside-toplevel,import-error
    from peft import LoraConfig
    from trl import SFTConfig, SFTTrainer
    # pylint: enable=import-outside-toplevel,import-error

    adapter = LoraConfig(r=config['lora_rank'], lora_alpha=2 * config['lora_rank'],
                         target_modules=['q_proj', 'v_proj'], lora_dropout=0.05,
                         bias='none', task_type='CAUSAL_LM', revision=revision)
    settings = SFTConfig(
        output_dir=str(output), max_length=config['max_length'], packing=False,
        per_device_train_batch_size=1, per_device_eval_batch_size=1,
        gradient_accumulation_steps=config['gradient_accumulation_steps'],
        gradient_checkpointing=True, gradient_checkpointing_kwargs={'use_reentrant': False},
        learning_rate=0.0002, num_train_epochs=1, max_steps=max_steps, fp16=True, bf16=False,
        optim='paged_adamw_8bit', eval_strategy='epoch', save_strategy='epoch', save_total_limit=1,
        logging_steps=5, report_to='none', push_to_hub=False, seed=config['seed'],
        completion_only_loss=True,
    )
    datasets = build_datasets(splits)
    return SFTTrainer(model=model, args=settings, processing_class=tokenizer,
                      train_dataset=datasets['train'], eval_dataset=datasets['validation'],
                      peft_config=adapter)


def train(config: dict, data_dir: Path, max_steps: int) -> Path:
    import torch  # pylint: disable=import-outside-toplevel,import-error

    output = HERE / 'outputs' / config['output_name']
    if output.exists():
        raise ValueError('Output already exists; choose a new output_name to preserve the run')
    report = preflight(config, data_dir)
    splits = load_splits(data_dir)
    model, tokenizer, revision = load_model(config, splits)
    trainer = build_trainer(config, output, model, tokenizer, splits, max_steps, revision)
    result = trainer.train()
    trainer.save_model(str(output))
    tokenizer.save_pretrained(str(output))
    report.update({'status': 'adapter trained; not published', 'resolved_revision': revision,
                   'config': config, 'training_metrics': result.metrics,
                   'validation_metrics': trainer.evaluate(), 'gpu': torch.cuda.get_device_name(0)})
    (output / 'run_manifest.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return output


def ensure_lengths(tokenizer, splits: dict, maximum: int) -> None:
    for name in ('train', 'validation'):
        for row in splits[name]:
            tokens = tokenizer.apply_chat_template(row['prompt'] + row['completion'], tokenize=True)
            if len(tokens) > maximum:
                raise ValueError(f'{name} exceeds max_length; do not silently truncate answers')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=HERE / 'config.json')
    parser.add_argument('--data', type=Path, default=HERE / 'data')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--max-steps', type=int, default=-1)
    args = parser.parse_args()
    if args.max_steps != -1 and args.max_steps < 1:
        parser.error('--max-steps must be positive, or -1 for one epoch')
    config = load_config(args.config)
    if args.dry_run:
        print(json.dumps(preflight(config, args.data), indent=2))
    else:
        print(train(config, args.data, args.max_steps))


if __name__ == '__main__':
    main()
