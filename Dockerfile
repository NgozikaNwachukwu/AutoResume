# syntax=docker/dockerfile:1
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git && rm -rf /var/lib/apt/lists/*

# Install BOTH runtime + dev test deps
COPY requirements.txt ./requirements.txt
COPY requirements-dev.txt ./requirements-dev.txt
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-dev.txt

# Bring code + tests + pytest config
COPY src ./src
COPY tests ./tests
COPY pyproject.toml ./pyproject.toml
COPY pytest.ini ./pytest.ini

# Default: run tests
CMD ["pytest", "-q"]
