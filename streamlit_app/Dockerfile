FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml .
RUN pip install uv && uv venv && uv pip install -e .

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["uv", "run", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"] 