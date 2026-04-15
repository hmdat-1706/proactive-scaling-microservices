FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY ai-scaler/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ai-scaler/ai_trainer.py .
COPY ai-scaler/ai_server.py .
COPY data/mock_dataset.csv . 

EXPOSE 8000
CMD ["uvicorn", "ai_server:app", "--host", "0.0.0.0", "--port", "8000"]
