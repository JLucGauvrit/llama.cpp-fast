FROM ubuntu:25.10
RUN apt-get update && apt-get install -y \
    git build-essential python3 python3-pip python3-venv cmake wget ca-certificates libcurl4-openssl-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt
RUN git clone https://github.com/ggml-org/llama.cpp.git && \
    cd llama.cpp && \
    mkdir build && cd build && \
    cmake .. && \
    cmake --build . --config Release

COPY quantize.sh /app/quantize.sh
RUN chmod +x /app/quantize.sh
CMD ["/app/quantize.sh"]
