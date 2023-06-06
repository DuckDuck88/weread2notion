#!/bin/bash

# 获取应用版本参数
version=$1

# 默认应用版本
default_version="latest"

# 如果没有指定版本参数，则使用默认版本
if [ -z "$version" ]; then
  version=$default_version
fi

# 容器名称
container_name="weread-to-notion"

# 检查是否存在同名容器
existing_container=$(docker ps -a --filter "name=$container_name" --format "{{.Names}}")

if [ ! -z "$existing_container" ]; then
  # 停止并删除同名容器
  echo "Stopping and removing existing container: $existing_container"
  docker stop "$existing_container"
  docker rm "$existing_container"
fi

echo "################ Building Docker image: $container_name:$version ################"
# 构建Docker镜像
docker build -t "$container_name:$version" .

echo "################ Starting Docker container: $container_name:$version ############"
# 启动容器
docker run -d -p 7000:80 --name "$container_name" "$container_name:$version"
