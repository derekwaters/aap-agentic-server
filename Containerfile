# podman build -t quay.io/rh-ee-dwaters/agentic-aap-demo:latest .
FROM registry.redhat.io/ubi9/python-311:latest

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY app/*.py ./app/

# Expose port if needed (optional, for HTTP server)
EXPOSE 8000

# Set environment variables (optional)
# ENV LLAMASTACK_URL=http://0.0.0.0:8321
# ENV REMOTE_AAP_MCP_URL=your-aap-mcp-url
# ENV LLAMASTACK_MODEL_ID=ollama/qwen3:4b

# NOTE: Run python main.py

CMD ["/bin/bash"]