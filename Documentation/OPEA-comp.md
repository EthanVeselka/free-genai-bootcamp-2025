# LLM Service Documentation

## Overview
This service provides a REST API for interacting with the DeepSeek-R1-Distill-Qwen-1.5B language model using vLLM as the backend. The service is containerized using Docker and handles model loading, inference, and response logging.

## Architecture

```
┌─────────────────┐
│  HTTP Request   │
│   (port 8000)   │
└────────┬────────┘
         │
┌────────▼────────┐
│  serve_model.py │
│   FastAPI App   │
├─────────────────┤
│    vLLM LLM    │
│ DeepSeek 1.5B  │
└────────┬────────┘
         │
┌────────▼────────┐
│  Response Logs  │
│     (JSONL)     │
└─────────────────┘
```

## File Structure

### Docker Configuration

#### Dockerfile
```dockerfile
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the service code
COPY serve_model.py .

# Run the service
CMD ["python3", "serve_model.py"]
```

#### docker-compose.yml
```yaml
services:
  llm-service:
    build: .
    runtime: nvidia
    ports:
      - "8000:8000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - ~/.cache/huggingface:/root/.cache/huggingface
      - .:/app/opea-comps
      - ./logs:/app/logs
```

## API Endpoints

### POST /v1/example-service
Generates text based on the provided prompt.

#### Request Format
```json
{
  "messages": "Your prompt text here"
}
```

#### Response Format
```json
{
  "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Generated response text"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

## Logging
The service logs all interactions to `logs/model_interactions.jsonl` in JSONL format:
```json
{
  "timestamp": "ISO-8601 timestamp",
  "prompt": "Input prompt",
  "response": "Model response",
  "model": "Model name",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 100
  }
}
```

## Setup and Usage

1. **Build the Container**:
```bash
docker compose build llm-service
```

2. **Start the Service**:
```bash
docker compose up llm-service
```

3. **Send a Request**:
```bash
curl http://localhost:8000/v1/example-service \
  -H "Content-Type: application/json" \
  -d '{
    "messages": "What is the meaning of life?"
  }'
```

## Model Configuration
The service uses vLLM with the following configuration:
- GPU Memory Utilization: 98%
- Max Model Length: 2048 tokens
- Max Batch Tokens: 2048
- Max Sequences: 128

## Dependencies
- vLLM
- FastAPI
- NVIDIA CUDA 12.1
- Python 3.x 