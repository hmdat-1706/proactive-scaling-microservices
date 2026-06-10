FROM python:3.11-slim
WORKDIR /app

# Install build-essential for compiling, remove immediately after to reduce attack surface
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker Layer Caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove build-essential linux-libc-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy application code and model
COPY ai_server.py .
COPY data_ingestion.py .
COPY model_retrain.py .
COPY ./prophet_model /app/prophet_model 

# Create non-root user and grant ownership of /app directory
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "ai_server:app", "--host", "0.0.0.0", "--port", "8000"]
