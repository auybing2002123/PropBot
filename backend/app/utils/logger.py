"""
日志配置模块
统一日志格式和级别管理
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


# 日志目录
LOG_DIR = Path(__file__).parent.parent.parent / "logs"


def setup_logging(debug: bool = False, name: Optional[str] = None) -> logging.Logger:
    """
    配置日志系统
    
    Args:
        debug: 是否开启调试模式，True 使用 DEBUG 级别，False 使用 INFO 级别
        name: 日志器名称，默认为 house_advisor
    
    Returns:
        配置好的 Logger 实例
    """
    logger_name = name or "house_advisor"
    level = logging.DEBUG if debug else logging.INFO
    
    # 日志格式：时间 | 级别 | 模块名 | 消息
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 获取或创建 logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)
    
    # 文件输出（滚动日志，最大 10MB，保留 5 个备份）
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            LOG_DIR / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"无法创建文件日志: {e}")
    
    # 阻止日志传播到根 logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = "house_advisor") -> logging.Logger:
    """
    获取已配置的 logger
    
    Args:
        name: 日志器名称
    
    Returns:
        Logger 实例
    """
    return logging.getLogger(name)
