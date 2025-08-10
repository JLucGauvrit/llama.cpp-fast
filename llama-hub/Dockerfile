# ===== Build CPU =====
FROM debian:stable AS build_cpu
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    git cmake build-essential libcurl4-openssl-dev && \
    rm -rf /var/lib/apt/lists/*
    
WORKDIR /opt
ARG LLAMA_CPP_REF=master
RUN git clone https://github.com/ggml-org/llama.cpp.git && cd llama.cpp && git checkout ${LLAMA_CPP_REF}
WORKDIR /opt/llama.cpp
RUN cmake -B build -DGGML_HTTP=ON -DLLAMA_BUILD_SERVER=ON && cmake --build build --config Release -j$(nproc)
RUN cp build/bin/llama-server /opt/llama-server-cpu

# ===== Build CUDA =====
FROM nvidia/cuda:12.4.1-devel-ubuntu22.04 AS build_cuda
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git cmake build-essential libcurl4-openssl-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /opt
ARG LLAMA_CPP_REF=master
RUN git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp && git checkout ${LLAMA_CPP_REF}

WORKDIR /opt/llama.cpp
# Remplacement de LLAMA_CUBLAS -> GGML_CUDA ; on force l’archi "native" (ou "all")
RUN cmake -B build \
    -DGGML_HTTP=ON \
    -DLLAMA_BUILD_SERVER=ON \
    -DGGML_CUDA=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CUDA_ARCHITECTURES=native && \
    cmake --build build --config Release -j"$(nproc)"

RUN cp build/bin/llama-server /opt/llama-server-cuda


# ===== Runtime =====
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3 python3-pip curl ca-certificates libstdc++6 libcurl4 && \
    rm -rf /var/lib/apt/lists/*

# Binaries
COPY --from=build_cpu  /opt/llama-server-cpu  /usr/local/bin/llama-server-cpu
COPY --from=build_cuda /opt/llama-server-cuda /usr/local/bin/llama-server-cuda

# App
WORKDIR /app
COPY app /app

RUN pip install --no-cache-dir fastapi uvicorn[standard] psutil jinja2 pydantic==2.* huggingface_hub==0.24.*

# Data
RUN mkdir -p /models
VOLUME ["/models"]

EXPOSE 8090 8080
ENV PYTHONUNBUFFERED=1

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]
