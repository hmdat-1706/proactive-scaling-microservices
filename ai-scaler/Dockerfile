# Dùng nền tảng Miniconda thay vì Python thuần
FROM continuumio/miniconda3:latest

WORKDIR /app

# Dùng conda tải bản Prophet đã được biên dịch sẵn lõi C++ (không bao giờ lỗi stan_backend)
RUN conda install -c conda-forge prophet pandas -y

# Tải các thư viện phụ bằng pip
RUN pip install requests prometheus_client

COPY ai_trainer.py .
COPY ai_server.py .
