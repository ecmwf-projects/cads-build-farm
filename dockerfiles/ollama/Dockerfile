FROM nvidia/cuda:12.2.0-base-ubuntu22.04
WORKDIR /opt/ollama
RUN apt-get update && apt-get install -y curl
RUN curl -L https://ollama.com/download/ollama-linux-amd64.tgz -o ollama-linux-amd64.tgz && \
    tar -C /usr -xzf ollama-linux-amd64.tgz && rm ollama-linux-amd64.tgz && \
    chmod +x /usr/bin/ollama
ENTRYPOINT [ "/usr/bin/ollama" ]
CMD ["serve"]