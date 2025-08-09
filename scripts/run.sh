#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BACKEND="${BACKEND:-$("$ROOT/scripts/detect-backend.sh")}"

# macOS: Docker ne voit PAS le GPU Apple. On lance en natif (Metal) si possible.
UNAME=$(uname -s || true)
if [[ "$UNAME" == "Darwin" ]]; then
  # si brew + llama.cpp dispo => serveur natif Metal
  if command -v llama-server >/dev/null 2>&1; then
    # variables .env lues si présentes
    set -a; [ -f .env ] && source .env; set +a
    MODEL_ARG=""
    if [[ -n "${MODEL_PATH:-}" ]]; then
      MODEL_ARG="-m ${MODEL_PATH}"
    elif [[ -n "${HF_REPO:-}" && -n "${HF_FILE:-}" ]]; then
      MODEL_ARG="--hf-repo ${HF_REPO} --hf-file ${HF_FILE}"
    else
      echo "⚠️  MODELE non défini (MODEL_PATH ou HF_*)."
      exit 1
    fi
    exec llama-server $MODEL_ARG --host 0.0.0.0 --port "${PORT:-8080}"
  fi
  # sinon: CPU via Docker
  BACKEND="cpu"
fi

echo "→ Backend: $BACKEND"
case "$BACKEND" in
  cuda)   PROFILE="cuda" ;;
  rocm)   PROFILE="rocm" ;;
  intel)  PROFILE="intel" ;;
  vulkan) PROFILE="vulkan" ;;
  *)      PROFILE="cpu" ;;
esac

# Expose GPU (CUDA) si besoin
EXTRA=()
if [[ "$PROFILE" == "cuda" ]]; then
  EXTRA+=(--profile cuda)
elif [[ "$PROFILE" == "rocm" ]]; then
  EXTRA+=(--profile rocm)
elif [[ "$PROFILE" == "intel" ]]; then
  EXTRA+=(--profile intel)
elif [[ "$PROFILE" == "vulkan" ]]; then
  EXTRA+=(--profile vulkan)
else
  EXTRA+=(--profile cpu)
fi

docker compose "${EXTRA[@]}" up -d
docker compose "${EXTRA[@]}" logs -f
