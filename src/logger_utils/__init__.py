"""
Кастомный логгер с поддержкой:
- Многопроцессной записи в файл (локальная разработка)
- Docker-окружения (только stdout)
"""

__all__ = ["get_logger"]

import logging
import os
from concurrent_log_handler import ConcurrentRotatingFileHandler
from typing import Optional, Union
from pathlib import Path


def get_logger(
    name: Optional[str] = None,
    level: Union[int, str] = logging.INFO,
    log_file: Optional[str] = None,
    docker_mode: Optional[bool] = None,
    fmt: str = '%(asctime)s | %(name)s | %(levelname)-8s | %(message)s'
) -> logging.Logger:
    """
    Создает и возвращает настроенный логер.
    
    Args:
        name: Имя логера
        level: Уровень логирования
        log_file: Путь к файлу лога (если None и не docker_mode, то logs/app.log)
        docker_mode: Режим Docker (если None, берется из DOCKER_ENV)
        fmt: Формат сообщений
    
    Returns:
        logging.Logger: Настроенный логер
    """
    # Устанавливаем уровень
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    # Создаем логер
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    
    # Создаем форматтер
    formatter = logging.Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S')
    
    if docker_mode:
        # Только stdout
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        console.setLevel(level)
        logger.addHandler(console)
    else:
        # Файл + консоль
        if log_file is None:
            log_file = str(Path("logs") / "app.log")
        
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Файловый handler
        file_handler = ConcurrentRotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8',
            use_gzip=True
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
        
        # Консоль (только сообщение, без формата)
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter('%(message)s'))
        console.setLevel(level)
        logger.addHandler(console)
    
    return logger