import json
import psutil
import platform
import shutil

try:
    import GPUtil
except Exception:
    GPUtil = None

out = {
    'platform': platform.platform(),
    'cpu_count': psutil.cpu_count(logical=False),
    'cpu_count_logical': psutil.cpu_count(logical=True),
    'mem_gb': round(psutil.virtual_memory().total / (1024**3), 2),
    'disk_gb': round(shutil.disk_usage('/').total / (1024**3), 2)
}

if GPUtil:
    gpus = GPUtil.getGPUs()
    out['gpus'] = []
    for g in gpus:
        out['gpus'].append({
            'id': g.id,
            'name': g.name,
            'vram_gb': round(g.memoryTotal / 1024, 2)
        })
else:
    out['gpus'] = []

print(json.dumps(out, indent=2))
# save to /data/specs.json if mounted
try:
    with open('/data/specs.json','w') as f:
        json.dump(out,f,indent=2)
except Exception:
    pass
    