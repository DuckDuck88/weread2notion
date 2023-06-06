bind = '0.0.0.0:80'  # 绑定的IP地址和端口号
# bind = '127.0.0.1:6000'  # 绑定的IP地址和端口号
workers = 4  # 工作进程的数量
worker_class = 'gevent'  # 使用gevent作为工作进程的类别
timeout = 600  # 超时时间，单位为秒
accesslog = '/var/log/weread'  # 访问日志的文件路径，'-' 表示输出到标准输出
errorlog = '/var/log/weread'  # 错误日志的文件路径，'-' 表示输出到标准输出
