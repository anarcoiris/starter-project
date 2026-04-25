#!/bin/bash

# Script to initialize Ollama with the required model for Symmetry
# This script should be run after the ollama container is up

MODEL_NAME="qwen2.5:3b"

echo "Waiting for Ollama to start..."
until curl -s http://ollama:11434/api/tags > /dev/null; do
  sleep 2
done

echo "Ollama is up! Pulling model: $MODEL_NAME..."
curl -X POST http://ollama:11434/api/pull -d "{\"name\": \"$MODEL_NAME\"}"

echo "Model $MODEL_NAME pull initiated/verified."
