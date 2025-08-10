import os, subprocess, signal, shutil, threading, time
from typing import Optional, Dict, Any
import psutil

from huggingface_hub import hf_hub_download

LLAMA_PORT = int(os.getenv("SERVER_PORT", "8080"))
HOST = os.getenv("HOST", "0.0.0.0")

THREADS = int(os.getenv("THREADS", "8"))
CTX_SIZE = int(os.getenv("CTX_SIZE", "4096"))
N_GPU_LAYERS = int(os.getenv("N_GPU_LAYERS", "99"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "256"))
UBATCH_SIZE = int(os.getenv("UBATCH_SIZE", "64"))

MODELS_DIR = "/models"

_proc: Optional[subprocess.Popen] = None
_proc_lock = threading.Lock()

def detect_capabilities() -> Dict[str, Any]:
    cpu_cores = os.cpu_count() or 1
    ram_bytes = psutil.virtual_memory().total
    ram_gb = round(ram_bytes / (1024**3), 2)

    # GPU NVIDIA
    has_gpu = False
    nvidia_paths = ["/dev/nvidiactl", "/proc/driver/nvidia/version"]
    if any(os.path.exists(p) for p in nvidia_paths):
        has_gpu = True
    # fallback: try nvidia-smi
    if not has_gpu:
        try:
            out = subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1)
            has_gpu = (out.returncode == 0)
        except Exception:
            pass

    return {
        "cpu_cores": cpu_cores,
        "ram_gb": ram_gb,
        "gpu_nvidia": has_gpu,
        "server_port": LLAMA_PORT,
        "ui_port": int(os.getenv("UI_PORT", "8090")),
        "defaults": {
            "threads": THREADS,
            "ctx_size": CTX_SIZE,
            "n_gpu_layers": N_GPU_LAYERS,
            "batch_size": BATCH_SIZE,
            "ubatch_size": UBATCH_SIZE,
        }
    }

def _select_binary(use_gpu: bool) -> str:
    # On préfère le binaire CUDA si GPU détecté et demandé.
    if use_gpu and shutil.which("nvidia-smi") is not None or os.path.exists("/dev/nvidiactl"):
        return "/usr/local/bin/llama-server-cuda"
    return "/usr/local/bin/llama-server-cpu"

def _ensure_model(repo_id: str, filename: str, hf_token: Optional[str]) -> str:
    os.makedirs(MODELS_DIR, exist_ok=True)
    dst = os.path.join(MODELS_DIR, filename)
    if os.path.exists(dst):
        return dst
    path = hf_hub_download(repo_id=repo_id, filename=filename, token=hf_token, local_dir=MODELS_DIR, local_dir_use_symlinks=False)
    # hf_hub_download retourne un chemin complet; si dans sous-répertoire, crée un lien/copier:
    if path != dst and os.path.exists(path):
        try:
            shutil.copy2(path, dst)
        except Exception:
            pass
    return dst if os.path.exists(dst) else path

def launch_llama(repo_id: str, filename: str, use_gpu: bool, overrides: Dict[str, Any], hf_token: Optional[str]) -> Dict[str, Any]:
    global _proc
    with _proc_lock:
        if _proc and _proc.poll() is None:
            # tuer l'ancien serveur proprement
            try:
                _proc.send_signal(signal.SIGINT)
                _proc.wait(timeout=3)
            except Exception:
                _proc.kill()

        model_path = _ensure_model(repo_id, filename, hf_token)

        threads = int(overrides.get("threads", THREADS))
        ctx = int(overrides.get("ctx_size", CTX_SIZE))
        n_gpu_layers = int(overrides.get("n_gpu_layers", N_GPU_LAYERS))
        batch = int(overrides.get("batch_size", BATCH_SIZE))
        ubatch = int(overrides.get("ubatch_size", UBATCH_SIZE))

        binary = _select_binary(use_gpu)
        cmd = [
            binary,
            "--model", model_path,
            "--host", HOST,
            "--port", str(LLAMA_PORT),
            "--ctx-size", str(ctx),
            "--threads", str(threads),
            "--embedding",
            "--parallel", "4",
            "--batch-size", str(batch),
            "--ubatch-size", str(ubatch)
        ]
        if "cuda" in binary:
            cmd += ["--n-gpu-layers", str(n_gpu_layers)]

        _proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # Démarre un fil pour drainer les logs (simple, évite blocage)
        def _drain():
            try:
                for line in _proc.stdout:
                    # on pourrait stocker les logs dans un fichier si besoin
                    pass
            except Exception:
                pass
        threading.Thread(target=_drain, daemon=True).start()

        # petite attente pour le /health
        time.sleep(0.8)

        return {"status": "starting", "binary": binary, "model": model_path, "port": LLAMA_PORT}

def stop_llama() -> Dict[str, Any]:
    global _proc
    with _proc_lock:
        if _proc and _proc.poll() is None:
            try:
                _proc.send_signal(signal.SIGINT)
                _proc.wait(timeout=3)
            except Exception:
                _proc.kill()
            finally:
                _proc = None
            return {"stopped": True}
        return {"stopped": False}
