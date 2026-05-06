FROM python:3.11-slim
WORKDIR /app

# build-essential
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Libs
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ai_server.py .

COPY ./prophet_model /app/prophet_model 

EXPOSE 8000
CMD ["uvicorn", "ai_server:app", "--host", "0.0.0.0", "--port", "8000"]
