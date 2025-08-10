FROM ubuntu:22.04
RUN apt-get update && apt-get install -y git build-essential ca-certificates
WORKDIR /opt
RUN git clone https://github.com/ggml-org/llama.cpp.git && cd llama.cpp && make -j
COPY run_server.sh /app/run_server.sh
RUN chmod +x /app/run_server.sh
CMD ["/app/run_server.sh"]
