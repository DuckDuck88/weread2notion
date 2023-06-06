# 基于 Python 官方镜像构建 Docker 镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 将当前目录下的所有文件复制到容器的 /app 目录下
COPY . /app

# 安装应用所需的依赖
RUN pip install -r requirements.txt

# 暴露容器的端口
EXPOSE 80

# 运行应用
CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]
