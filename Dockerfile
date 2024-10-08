# 使用支持多平台的基础镜像
FROM --platform=$BUILDPLATFORM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到容器中的/app
COPY . /app

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露Streamlit默认端口
EXPOSE 8501

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 运行Streamlit应用
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]