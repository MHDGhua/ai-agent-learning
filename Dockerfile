# 选择一个轻量级的 Python 基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 将项目的核心代码（first_agent 文件夹）和依赖文件复制到镜像中
COPY first_agent/ ./first_agent/
COPY requirements.txt .

# 设置 pip 使用清华源，加速依赖安装
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 暴露 Streamlit 默认的 8501 端口
EXPOSE 8501

# 定义容器启动时运行的命令
# 这里特别设置了 server.address=0.0.0.0，让容器能接收外部访问
CMD ["streamlit", "run", "first_agent/app.py", "--server.port=8501", "--server.address=0.0.0.0"]