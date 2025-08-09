#!/usr/bin/env bash
set -euo pipefail

# par défaut
BACKEND="cpu"

# 1) CUDA (Linux/WSL2 + NVIDIA)
if command -v nvidia-smi >/dev/null 2>&1; then
  BACKEND="cuda"
fi

# 2) ROCm (Linux + AMD)
if [[ "$BACKEND" == "cpu" ]] && (command -v rocminfo >/dev/null 2>&1 || /opt/rocm/bin/rocminfo >/dev/null 2>&1); then
  BACKEND="rocm"
fi

# 3) Intel/SYCL (Linux avec oneAPI/Level-Zero dispo)
if [[ "$BACKEND" == "cpu" ]] && lspci 2>/dev/null | grep -qi 'Intel.*Graphics'; then
  BACKEND="intel"
fi

# 4) Vulkan (dernier recours GPU générique)
if [[ "$BACKEND" == "cpu" ]] && command -v vulkaninfo >/dev/null 2>&1; then
  BACKEND="vulkan"
fi

echo "$BACKEND"
