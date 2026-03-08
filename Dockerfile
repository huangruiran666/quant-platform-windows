
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装依赖
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# 复制源码
COPY . .

# 启动主程序
CMD ["python", "dual_cloud_quant_v4.py"]
