# OPEA Components Service

A service for running large language models using vLLM for optimized inference.

## Model Service

The service uses the Qwen 1.5B model (`deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B`) with vLLM for efficient serving. You will need to have it downloaded with Huggingface to use.

### Getting Started

Run the model service:

```bash
# Set environment variables
export LLM_SERVICE_HOST_IP="0.0.0.0"
export LLM_SERVICE_PORT=8000

# Run the service
python serve_model.py
```

### Configuration Parameters

The model is configured with optimized parameters for single GPU deployment:

- `tensor_parallel_size`: Controls model parallelism across GPUs (default: 1)
- `gpu_memory_utilization`: GPU memory usage (default: 0.90)
- `max_model_len`: Maximum sequence length (default: 2048)
- `max_num_batched_tokens`: Batch size limit (default: 2048)
- `max_num_seqs`: Maximum parallel sequences (default: 128)

## API Endpoints

- `/v1/generate`: Main generation endpoint
- `/v1/example-service`: Example service endpoint

## Logging

Logs are stored in `logs/model_interactions.jsonl` and include:
- Timestamps
- Prompts
- Responses
- Model parameters
- Error logs

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| LLM_SERVICE_HOST_IP | Service host IP | 0.0.0.0 |
| LLM_SERVICE_PORT | Service port | 8000 |

## References

- [vLLM Documentation](https://vllm.readthedocs.io/)