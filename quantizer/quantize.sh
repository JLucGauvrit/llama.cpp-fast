#!/usr/bin/env bash
set -e
# modèle attendu: /models/<owner>_<model> (clone snapshot)
MODEL_DIR=$(ls /models | head -n1)
MODEL_PATH="/models/$MODEL_DIR"
GGML_OUT="${MODEL_PATH}/model_q4.bin"

echo "Model dir: $MODEL_PATH"

# rechercher fichier safetensors ou pytorch model
# Ce script illustre l'appel à l'outil de quantize fourni par llama.cpp
cd /opt/llama.cpp
# on suppose qu'un script util/convert.py ou un binaire de quantize est disponible
# Utiliser quantize dans llama.cpp (ex: ./quantize + input file)

# Recherche d'un fichier poids commun
WEIGHT_FILE=$(find $MODEL_PATH -type f -name "*.safetensors" -o -name "*.bin" | head -n1)
if [ -z "$WEIGHT_FILE" ]; then
  echo "No weight file found in $MODEL_PATH"
  exit 1
fi

echo "Found weight file: $WEIGHT_FILE"

# Exemple d'appel : (adapté selon release llama.cpp)
# ./quantize $WEIGHT_FILE $GGML_OUT q4_0
# Si l'outil n'existe pas, cet endroit montre le point où il faut appeler l'outil de quantize.

if [ -x ./quantize ]; then
  echo "Running quantize binary..."
  ./quantize $WEIGHT_FILE $GGML_OUT q4_0
  echo "Quantization done: $GGML_OUT"
else
  echo "quantize binary not found in /opt/llama.cpp. Please check llama.cpp version."
  exit 1
fi
