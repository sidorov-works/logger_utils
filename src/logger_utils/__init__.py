# logger_utils/__init__.py

"""
Кастомный логгер с поддержкой:
- Многопроцессной записи в файл (локальная разработка)
- Docker-окружения (только stdout)
- Автоматической подстановки имени процесса через обертку корневого логера
"""

__all__ = ["get_logger"]

import logging
import os
from concurrent_log_handler import ConcurrentRotatingFileHandler
from typing import Optional, Union
from functools import wraps
from pathlib import Path

_configured = False


def get_logger(
    name: Optional[str] = None,
    process_name: Optional[str] = None,
    level: Union[int, str] = logging.INFO,
    log_file: Optional[str] = None,
    docker_mode: Optional[bool] = None,
    fmt: str = '%(asctime)s | %(process_name)-15s | %(name)-30s | %(levelname)-8s | %(message)s'
) -> logging.Logger:
    """
    Возвращает логер. При первом вызове настраивает корневой логер.
    
    Args:
        name: Имя логера
        process_name: Имя процесса (подставляется в поле process_name каждого сообщения)
        level: Уровень логирования (только при первом вызове)
        log_file: Путь к файлу (только при первом вызове)
        docker_mode: Режим Docker (только при первом вызове)
        fmt: Формат сообщений (только при первом вызове)
    """
    global _configured
    
    # Первый вызов - настройка корневого логера
    if not _configured:
        _configured = True
        
        if docker_mode is None:
            docker_mode = os.environ.get('DOCKER_ENV') == 'true'
        
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        root_logger.handlers.clear()
        
        formatter = logging.Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S')
        
        if docker_mode:
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            root_logger.addHandler(console)
        else:
            if log_file is None:
                log_file = str(Path("logs") / "app.log")
            
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            file_handler = ConcurrentRotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,
                backupCount=5,
                encoding='utf-8',
                use_gzip=True
            )
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            
            console = logging.StreamHandler()
            console.setFormatter(logging.Formatter('%(message)s'))
            root_logger.addHandler(console)
    
    # Если указан process_name - оборачиваем корневой логер
    if process_name:
        root_logger = logging.getLogger()
        
        def wrap_method(method):
            @wraps(method)
            def wrapper(msg, *args, **kwargs):
                extra = kwargs.get('extra', {})
                extra['process_name'] = process_name
                kwargs['extra'] = extra
                return method(msg, *args, **kwargs)
            return wrapper
        
        for method_name in ['debug', 'info', 'warning', 'error', 'critical']:
            if hasattr(root_logger, method_name):
                setattr(root_logger, method_name, wrap_method(getattr(root_logger, method_name)))
    
    return logging.getLogger(name)