from loguru import logger
import sys

#清空所有已注册的 handler，让你从头配置自己的输出。否则会有默认的handler导致重复混乱
logger.remove()
#把日志打印在终端；设置日志格式、终端显示的级别
logger.add(sys.stdout, format="{time:HH:mm:ss} | {level} | {message}", level="INFO")
#把日志存储到文件； 设置日志大于500mb轮转、日志存储的级别
logger.add("agent.log", rotation="500 MB", level="DEBUG")