#!/usr/bin/env bash
set -e
MODEL_DIR=$(ls /models | head -n1)
MODEL_BIN="/models/$MODEL_DIR/model_q4.bin"

if [ ! -f "$MODEL_BIN" ]; then
  echo "Quantized model not found at $MODEL_BIN"
  exit 1
fi

cd /opt/llama.cpp
# Exemple d'utilisation: lancer le serveur http (selon la version de llama.cpp)
# ./main -m $MODEL_BIN --server --port 8080

if [ -x ./main ]; then
  echo "Starting llama.cpp main with model $MODEL_BIN"
  ./main -m "$MODEL_BIN" --server --port 8080
else
  echo "llama.cpp main binary missing"
  exit 1
fi
