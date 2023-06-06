# 基于 Python 官方镜像构建 Docker 镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 单独复制 requirements.txt，后续可以利用 Docker 缓存避免重复安装依赖
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt


# 将当前目录下的所有文件复制到容器的 /app 目录下
COPY . /app
# 暴露容器的端口
EXPOSE 80

# 运行应用
CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]
