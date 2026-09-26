"""Publish only the reviewed adapter artifacts to the author's Hugging Face profile."""

from pathlib import Path

from huggingface_hub import HfApi


ROOT = Path(__file__).resolve().parents[2]
ADAPTER_DIR = (ROOT / 'model' / 'finetune' / 'outputs' /
               'Ministral-3-3B-turing-a1-qlora-v1')
REPO_ID = 'kageskull/Ministral-3-3B-turing-a1-qlora-v1'
UPLOAD_FILES = (
    'README.md',
    'adapter_model.safetensors',
    'adapter_config.json',
    'chat_template.jinja',
    'tokenizer.json',
    'tokenizer_config.json',
)


def publish(api=None):
    """Verify account and artifact set, then create a new public adapter repo."""
    client = api or HfApi()
    identity = client.whoami()
    if identity.get('name', '').casefold() != 'kageskull':
        raise ValueError('The active Hugging Face login is not kageskull')
    missing = [name for name in UPLOAD_FILES if not (ADAPTER_DIR / name).is_file()]
    if missing:
        raise FileNotFoundError(f'Missing adapter publication files: {missing}')
    client.create_repo(repo_id=REPO_ID, repo_type='model', private=False, exist_ok=False)
    client.upload_folder(repo_id=REPO_ID, repo_type='model', folder_path=ADAPTER_DIR,
                         allow_patterns=list(UPLOAD_FILES),
                         commit_message='Publish fine-tuned Ministral adapter')
    repository = client.repo_info(REPO_ID, repo_type='model')
    if repository.private:
        raise RuntimeError('The Hugging Face repository was created as private')
    return f'https://huggingface.co/{REPO_ID}'


if __name__ == '__main__':
    result = publish()
    print(result)
