# 🐳 Illacme-plenipes Industrial Dockerfile
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装必要的系统构建工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 预拷贝依赖以利用 Docker 缓存
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 拷贝全量源代码
COPY . .

# 环境标识
ENV PLENIPES_DOCKER=1
ENV PYTHONUNBUFFERED=1

# 暴露主权端口序列
EXPOSE 43210 43211 43212

# 默认启动 API 模式
ENTRYPOINT ["python", "plenipes.py"]
CMD ["--api", "--api-port", "43211"]
