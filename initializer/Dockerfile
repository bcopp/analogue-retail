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
    poetry install --no-interaction --no-root

# Copy source code
COPY ./ ./

# Set environment variables
ENV PYTHONPATH=/app

# Expose port 8000
EXPOSE 8000
EXPOSE 4566
EXPOSE 3306


# Run the initializer
CMD ["poetry", "run", "python", "initialize_database.py"] 