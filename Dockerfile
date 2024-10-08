# 使用官方的 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到容器中的/app目录
COPY . /app

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露 Streamlit 默认端口
EXPOSE 8501

# 运行 Streamlit 应用
CMD ["streamlit", "run", "main.py"]