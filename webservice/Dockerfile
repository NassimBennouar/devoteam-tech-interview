FROM python:3.13-slim

WORKDIR /webservice

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install uv && uv venv && uv pip install -e .

COPY . .

EXPOSE 8000

CMD ["uv", "run", "python", "main.py"]