FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    git build-essential python3 python3-pip python3-venv cmake wget ca-certificates libcurl4-openssl-dev && \
    rm -rf /var/lib/apt/lists/*
    
WORKDIR /opt

RUN git clone https://github.com/ggml-org/llama.cpp.git && \
    cd llama.cpp && \
    mkdir build && cd build && \
    cmake .. && \
    cmake --build . --config Release

COPY run_server.sh /app/run_server.sh
RUN chmod +x /app/run_server.sh
CMD ["/app/run_server.sh"]
