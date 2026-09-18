"""Serve a locally trained adapter through the simulator's chat-completions contract."""

import argparse
import json
import os
from pathlib import Path
import secrets
import threading

from flask import Flask, jsonify, request


class InferenceEngine:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.lock = threading.Lock()

    def complete(self, messages, max_tokens):
        import torch  # pylint: disable=import-outside-toplevel,import-error

        with self.lock, torch.inference_mode():
            inputs = self.tokenizer.apply_chat_template(
                messages, tokenize=True, add_generation_prompt=True,
                return_dict=True, return_tensors='pt',
            ).to(self.model.device)
            count = inputs['input_ids'].shape[-1]
            if count > 4096:
                raise ValueError('Input exceeds the local 4096-token context budget')
            outputs = self.model.generate(**inputs, max_new_tokens=max_tokens, do_sample=False)
            return self.tokenizer.decode(outputs[0][count:], skip_special_tokens=True)


def load_adapter(directory: Path):
    # pylint: disable=import-outside-toplevel,import-error
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    # pylint: enable=import-outside-toplevel,import-error

    manifest = json.loads((directory / 'run_manifest.json').read_text(encoding='utf-8'))
    if manifest['status'] != 'adapter trained; not published':
        raise ValueError('Expected a completed training manifest')
    if not torch.cuda.is_available():
        raise ValueError('This local adapter server requires CUDA')
    quantization = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                                     bnb_4bit_use_double_quant=True,
                                     bnb_4bit_compute_dtype=torch.float16)
    base = AutoModelForCausalLM.from_pretrained(
        manifest['base_model'], revision=manifest['resolved_revision'],
        quantization_config=quantization, device_map={'': 0}, torch_dtype=torch.float16,
    )
    model = PeftModel.from_pretrained(base, directory)
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(directory)
    return InferenceEngine(model, tokenizer), manifest['output_name']


def validate_request(body, model_id):
    if not isinstance(body, dict) or body.get('model') != model_id or body.get('stream'):
        raise ValueError('Expected the configured model and a non-streaming request')
    messages = body.get('messages')
    if not isinstance(messages, list) or not 1 <= len(messages) <= 20:
        raise ValueError('Expected 1–20 chat messages')
    for message in messages:
        if (not isinstance(message, dict)
                or message.get('role') not in ('system', 'user', 'assistant')
                or not isinstance(message.get('content'), str)):
            raise ValueError('Invalid chat message')
    max_tokens = body.get('max_tokens', 512)
    if (not isinstance(max_tokens, int) or isinstance(max_tokens, bool)
            or not 1 <= max_tokens <= 512):
        raise ValueError('max_tokens must be an integer in [1, 512]')
    return messages, max_tokens


def create_server(engine, model_id, api_key=''):
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 65_536

    @app.post('/v1/chat/completions')
    def complete():
        if api_key and not secrets.compare_digest(request.headers.get('Authorization', ''),
                                                   'Bearer ' + api_key):
            return jsonify({'error': 'Authentication required'}), 401
        try:
            messages, max_tokens = validate_request(request.get_json(silent=True), model_id)
            content = engine.complete(messages, max_tokens)
        except ValueError as exc:
            return jsonify({'error': str(exc)}), 400
        return jsonify({'model': model_id, 'choices': [
            {'index': 0, 'message': {'role': 'assistant', 'content': content},
             'finish_reason': 'stop'},
        ]})

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adapter', type=Path, required=True)
    arguments = parser.parse_args()
    inference, name = load_adapter(arguments.adapter)
    create_server(inference, name, os.environ.get('TURING_MODEL_API_KEY', '')).run(
        host='127.0.0.1', port=8080, debug=False,
    )
