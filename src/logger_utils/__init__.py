# logger_utils/__init__.py

"""
Кастомный логгер с поддержкой:
- Многопроцессной записи в файл (локальная разработка)
- Docker-окружения (только stdout)
- Автоматической подстановки имени процесса через фильтр
"""

__all__ = ["get_logger"]

import logging
import os
from concurrent_log_handler import ConcurrentRotatingFileHandler
from typing import Optional, Union
from pathlib import Path

_configured = False
_process_name = None


class ProcessNameFilter(logging.Filter):
    """Добавляет process_name в каждую запись лога"""
    def filter(self, record):
        record.process_name = _process_name or "unknown"
        return True


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
        process_name: Имя процесса. Если не указан, берется из name
        level: Уровень логирования (только при первом вызове)
        log_file: Путь к файлу (только при первом вызове)
        docker_mode: Режим Docker (только при первом вызове)
        fmt: Формат сообщений (только при первом вызове)
    """
    global _configured, _process_name
    
    # Если process_name не указан, берем из name
    if process_name is None and name is not None:
        process_name = name
    
    # Запоминаем process_name для фильтра
    if process_name:
        _process_name = process_name
    
    # Первый вызов - настройка корневого логера
    if not _configured:
        _configured = True
        
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        root_logger.handlers.clear()
        
        # Добавляем фильтр
        root_logger.addFilter(ProcessNameFilter())
        
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
    
    return logging.getLogger(name)