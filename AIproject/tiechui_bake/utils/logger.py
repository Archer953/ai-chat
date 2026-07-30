# 日志配置工具
import logging
import os

def setup_logger():
    """全局日志配置（只需调用一次）"""
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)

    # 配置日志格式
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(r'logs\app.log')
        ]
    )