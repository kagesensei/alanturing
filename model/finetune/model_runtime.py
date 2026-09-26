"""Load verified text weights from a pinned base checkpoint for training and chat."""

from pathlib import Path


CACHE = Path(__file__).resolve().parents[1] / 'base'


def check_loaded_weights(report):
    """Never train accidentally initialized weights after a checkpoint conversion."""
    if report.get('missing_keys') or report.get('mismatched_keys') or report.get('error_msgs'):
        raise ValueError(f'Incomplete base checkpoint load: {report}')
    unexpected = report.get('unexpected_keys', [])
    if any(not key.startswith(('vision_tower.', 'multi_modal_projector.'))
           for key in unexpected):
        raise ValueError(f'Unexpected language weights: {unexpected}')


def load_text_model(model_id, revision, offline=False):
    # Optional GPU stack is imported only when loading real weights.
    # pylint: disable=import-outside-toplevel,import-error
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM, BitsAndBytesConfig
    # pylint: enable=import-outside-toplevel,import-error

    if not torch.cuda.is_available():
        raise ValueError('CUDA-enabled PyTorch and a compatible GPU are required')
    config = AutoConfig.from_pretrained(model_id, revision=revision, cache_dir=CACHE,
                                       local_files_only=offline)
    options = {}
    if config.model_type == 'mistral3':
        config = config.text_config
        # The official BF16 checkpoint stores text weights under this prefix.
        # Vision weights are intentionally unused in this text-only application.
        options['key_mapping'] = {r'^language_model\.': ''}
    quantization = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                                     bnb_4bit_use_double_quant=True,
                                     bnb_4bit_compute_dtype=torch.float16)
    model, report = AutoModelForCausalLM.from_pretrained(
        model_id, revision=revision, config=config, quantization_config=quantization,
        device_map={'': 0}, dtype=torch.float16, attn_implementation='sdpa',
        cache_dir=CACHE, local_files_only=offline, output_loading_info=True, **options,
    )
    check_loaded_weights(report)
    return model
