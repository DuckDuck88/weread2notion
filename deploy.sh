#!/bin/bash

# 获取应用版本参数
version=$1

# 默认应用版本
default_version="latest"

# 如果没有指定版本参数，则使用默认版本
if [ -z "$version" ]; then
  version=$default_version
fi

# 构建Docker镜像
docker build -t weread-to-notion:$version .

# 启动容器
docker run -d  -p 7000:80 weread-to-notion:$version
