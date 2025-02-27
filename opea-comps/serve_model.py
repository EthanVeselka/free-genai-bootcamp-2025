from fastapi import HTTPException
from comps.cores.proto.api_protocol import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatMessage,
    UsageInfo
)
from comps.cores.mega.constants import ServiceType, ServiceRoleType
from comps import MicroService, ServiceOrchestrator
from vllm import LLM, SamplingParams  # Add vLLM imports
import os
import json
import datetime

# Environment variables for service configuration
LLM_SERVICE_HOST_IP = os.getenv("LLM_SERVICE_HOST_IP", "0.0.0.0")
LLM_SERVICE_PORT = os.getenv("LLM_SERVICE_PORT", 8000)

# Model configuration
MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"

class ExampleService:
    def __init__(self, host="0.0.0.0", port=8000):
        print('Starting service and loading model...')
        os.environ["TELEMETRY_ENDPOINT"] = ""
        self.host = host
        self.port = port
        self.endpoint = "/v1/example-service"
        self.megaservice = ServiceOrchestrator()
        
        # Set up logging file with relative path
        self.log_file = "logs/model_interactions.jsonl"
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Load the model with more aggressive memory settings
        self.model = LLM(
            model=MODEL_NAME,
            gpu_memory_utilization=0.90,  # Use almost all GPU memory
            tensor_parallel_size=1,
            max_model_len=2048,          # Further reduced max sequence length
            max_num_batched_tokens=2048,  # Reduced batch size
            max_num_seqs=128,            # Reduced parallel sequences
            trust_remote_code=True
        )
        print(f'Model {MODEL_NAME} loaded successfully')

    def add_remote_service(self):
        # Configure the LLM service
        llm = MicroService(
            name="llm",
            host=LLM_SERVICE_HOST_IP,
            port=LLM_SERVICE_PORT,
            endpoint="/v1/generate",
            use_remote_service=True,
            service_type=ServiceType.LLM,
        )
        self.megaservice.add(llm)

    def start(self):
        self.service = MicroService(
            self.__class__.__name__,
            service_role=ServiceRoleType.MEGASERVICE,
            host=self.host,
            port=self.port,
            endpoint=self.endpoint,
            input_datatype=ChatCompletionRequest,
            output_datatype=ChatCompletionResponse,
        )

        self.service.add_route(self.endpoint, self.handle_request, methods=["POST"])
        self.service.start()

    async def handle_request(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        try:
            print(f"Received request: {request.messages}")  # Debug log
            
            # Create sampling parameters for the model
            sampling_params = SamplingParams(
                temperature=0.7,
                max_tokens=100
            )
            
            print("Generating response...")  # Debug log
            # Generate response using the loaded model
            outputs = self.model.generate(request.messages, sampling_params)
            content = outputs[0].outputs[0].text
            print(f"Generated content: {content}")  # Debug log

            # Log the interaction
            interaction = {
                "timestamp": datetime.datetime.now().isoformat(),
                "prompt": request.messages,
                "response": content,
                "model": MODEL_NAME,
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            }
            
            print(f"Attempting to write to: {self.log_file}")
            
            # Test if directory exists and is writable
            log_dir = os.path.dirname(self.log_file)
            print(f"Log directory: {log_dir}")
            print(f"Directory exists: {os.path.exists(log_dir)}")
            print(f"Directory writable: {os.access(log_dir, os.W_OK)}")
            
            try:
                with open(self.log_file, "a") as f:
                    f.write(json.dumps(interaction) + "\n")
                print("Response logged.")
            except Exception as write_error:
                print(f"Error writing to file: {str(write_error)}")

            # Format the response
            response = ChatCompletionResponse(
                model=MODEL_NAME,
                choices=[
                    ChatCompletionResponseChoice(
                        index=0,
                        message=ChatMessage(
                            role="assistant",
                            content=content
                        ),
                        finish_reason="stop"
                    )
                ],
                usage=UsageInfo(
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0
                )
            )
            
            return response
            
        except Exception as e:
            # Log the error too
            error_log = {
                "timestamp": datetime.datetime.now().isoformat(),
                "prompt": request.messages,
                "error": str(e),
                "model": MODEL_NAME
            }
            with open(self.log_file, "a") as f:
                f.write(json.dumps(error_log) + "\n")
            
            raise HTTPException(status_code=500, detail=str(e))

# Initialize and start the service
if __name__ == "__main__":
    example = ExampleService()
    example.add_remote_service()
    example.start()

