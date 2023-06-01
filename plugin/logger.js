const winston = require('winston');

// 创建日志器实例
const logger = winston.createLogger({
    transports: [
        new winston.transports.Console(),
    ],
    exceptionHandlers: [
        new winston.transports.Console(),
    ],
});

// // 设置 handleExceptions 属性
// logger.exceptions.handle(
//     new winston.transports.Console()
// );

// // 示例日志输出
// logger.info('This is an informational message.');
// logger.error('An error occurred.');
//
// // 处理未捕获的异常
// process.on('uncaughtException', (err) => {
//     logger.error(`Uncaught Exception: ${err.message}`);
//     // 其他处理逻辑...
// });
