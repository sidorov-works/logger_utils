# logger_utils/__init__.py

"""
Кастомный логгер с поддержкой:
- Многопроцессной записи в файл (локальная разработка)
- Docker-окружения (только stdout)
- Управления уровнем логирования через config.LOGGING_LEVEL
- Автоматической подстановки process_name через декоратор
"""

# Это то, что будет доступно при импорте "from logger_utils import *"
__all__ = [
    "get_logger"
    "wrap_logger_methods"
    "configure_root"
]

import logging
import os
from concurrent_log_handler import ConcurrentRotatingFileHandler
from typing import Optional, Union
from functools import wraps
from pathlib import Path


def configure_root(
    level: Union[int, str] = logging.INFO,
    log_file: Optional[str] = None,
    docker_mode: Optional[bool] = None,
    fmt: str = '%(asctime)s | %(levelname)-8s | %(process_name)-12s | %(message)s'
) -> None:
    """
    Настраивает корневой логер для всего приложения.
    """
    # Определяем режим
    if docker_mode is None:
        docker_mode = os.environ.get('DOCKER_ENV') == 'true'
    
    # Устанавливаем уровень
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    # Получаем корневой логер
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()  # убираем стандартные
    
    # Создаем форматтер
    formatter = logging.Formatter(fmt)
    
    if docker_mode:
        # Только stdout
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        console.setLevel(level)
        root_logger.addHandler(console)
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
        root_logger.addHandler(file_handler)
        
        # Консоль
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter('%(message)s'))
        console.setLevel(level)
        root_logger.addHandler(console)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Просто получает логер, настройки уже применены к корню.
    """
    return logging.getLogger(name)


def wrap_logger_methods(logger, worker_name: str):
    """Декоратор для автоматической подстановки process_name в extra-поля"""
    def proc_name_dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Безопасно добавляем process_name в extra, сохраняя существующие поля
            extra = kwargs.get('extra', {})
            extra['process_name'] = worker_name
            kwargs['extra'] = extra
            return func(*args, **kwargs)
        return wrapper
    
    # Применяем ко всем методам логирования
    for method_name in ['debug', 'info', 'warning', 'error', 'critical']:
        method = getattr(logger, method_name)
        setattr(logger, method_name, proc_name_dec(method))
    
    return logger