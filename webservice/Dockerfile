FROM python:3.13-slim

WORKDIR /webservice

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
EXPOSE 8000

# Run the application with uv
CMD ["uv", "run", "python", "main.py"]