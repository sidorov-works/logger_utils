# logger_utils/__init__.py

__all__ = ["get_logger"]

import logging
import os
from concurrent_log_handler import ConcurrentRotatingFileHandler
from typing import Optional, Union
from pathlib import Path

_configured = False


def get_logger(
    name: Optional[str] = None,
    level: Union[int, str] = logging.INFO,
    log_file: Optional[str] = None,
    docker_mode: Optional[bool] = None,
    fmt: str = '%(asctime)s | %(name)-30s | %(levelname)-8s | %(message)s'
) -> logging.Logger:
    """
    Возвращает логер. При первом вызове настраивает корневой логер.
    """
    global _configured
    
    if not _configured:
        _configured = True
        
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
    
    return logging.getLogger(name)