FROM python:3.11-slim
WORKDIR /app

# Cài đặt build-essential để hỗ trợ compile các thư viện Python nếu cần
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements trước để tận dụng Docker Layer Caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code và model vào
COPY ai_server.py .
COPY data_ingestion.py .
COPY model_retrain.py .
COPY ./prophet_model /app/prophet_model 

# Tạo user không có quyền root và cấp quyền sở hữu thư mục /app cho user đó
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "ai_server:app", "--host", "0.0.0.0", "--port", "8000"]
