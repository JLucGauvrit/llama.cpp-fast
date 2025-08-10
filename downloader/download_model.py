import os
from huggingface_hub import snapshot_download

HF_TOKEN = os.environ.get('HF_TOKEN')
MODEL_ID = os.environ.get('MODEL_ID','meta-llama/Llama-2-7b-chat-hf')
OUTDIR = '/models/'+MODEL_ID.replace('/','_')

print('Downloading', MODEL_ID, 'to', OUTDIR)

snapshot_download(repo_id=MODEL_ID, cache_dir='/models', token=HF_TOKEN)
print('Done')
