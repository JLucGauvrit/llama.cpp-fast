FROM ubuntu:latest

# Install dependencies
# This Dockerfile installs necessary packages for building llama.cpp
# and sets up the environment for building the project.
RUN apt-get update && \
    apt-get install -y git libcurl4-openssl-dev cmake build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Copy the build script into the container
COPY build.sh /workspace/build.sh

RUN chmod +x build.sh && ./build.sh

CMD [ "bash" ]
