#!/bin/bash

set -euo pipefail

git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp 

cmake -B build
cmake --build build --config Release
