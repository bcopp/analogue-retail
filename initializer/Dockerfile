FROM python:3.9-slim

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
    poetry install --no-interaction --no-root

# Copy source code
COPY ./ ./

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Set proper permissions
RUN chown -R appuser:appuser /app

# Set PYTHONPATH to /app so Python can find modules in the application directory
ENV PYTHONPATH=/app

# Switch to non-root user
USER appuser

# Run the initializer
CMD ["python", "initialize_database.py"] 