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