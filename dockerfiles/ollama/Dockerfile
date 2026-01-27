FROM nvidia/cuda:12.2.0-base-ubuntu22.04
WORKDIR /opt/ollama
RUN apt-get update && apt-get install -y curl zstd
RUN sh -c "curl -fsSL https://ollama.com/download/ollama-linux-amd64.tar.zst | tar x --zstd -C /usr" && \
    chmod +x /usr/bin/ollama
ENTRYPOINT [ "/usr/bin/ollama" ]
CMD ["serve"]