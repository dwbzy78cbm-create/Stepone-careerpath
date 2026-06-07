FROM python:3.11-slim

WORKDIR /app

# 复制依赖并安装
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ ./backend/

# 复制 web-demo 静态文件
COPY web-demo/ ./web-demo/

# 工作目录
WORKDIR /app/backend

# 暴露端口
EXPOSE 8000
EXPOSE 80

# 启动服务（同时监听 8000 和 80）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
