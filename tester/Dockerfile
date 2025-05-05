FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root --no-dev

# Copy source code
COPY ./ ./

# Set environment variables
ENV PYTHONPATH=/app

# Run the tester
CMD ["poetry", "run", "python", "tester.py"] 