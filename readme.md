# logger-utils

Утилита для настройки логирования в Python-приложениях с поддержкой многопроцессной записи и Docker-окружения.

## Возможности

- **Многопроцессная ротация файлов** — через `ConcurrentRotatingFileHandler` (без гонок)
- **Docker-режим** — автоматическое переключение на stdout при `DOCKER_ENV=true`
- **Гибкая настройка** — каждый логер создается с собственными параметрами
- **Автоматическое создание директорий** — при указании пути к файлу
- **Отсутствие глобального состояния** — нет зависимости от конфигов проекта

## Установка

```bash
pip install git+https://github.com/sidorov-works/logger_utils@v0.2.0
```

## Использование

### 1. Создание логера в модуле

```python
from logger_utils import get_logger

# Простой вариант — использует настройки по умолчанию
logger = get_logger(__name__)

logger.info("Сообщение")
logger.error("Ошибка", exc_info=True)
```

### 2. С кастомными параметрами

```python
from logger_utils import get_logger
from pathlib import Path

logger = get_logger(
    name="MY_SERVICE",
    level="DEBUG",
    log_file=str(Path("logs") / "service.log"),
    docker_mode=False,  # принудительно файл
    fmt='%(asctime)s | %(name)s | %(levelname)-8s | %(message)s'
)
```

### 3. В Docker-окружении

```yaml
# docker-compose.yml
services:
  app:
    environment:
      - DOCKER_ENV=true  # переключает на stdout
```

В коде:
```python
logger = get_logger(__name__)  # автоматически определит DOCKER_ENV
```

## API

### `get_logger(name=None, level=logging.INFO, log_file=None, docker_mode=None, fmt=None)`

Создает и возвращает настроенный логер.

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `name` | `str` или `None` | `None` | Имя логера. Если `None`, возвращает корневой логер |
| `level` | `int` или `str` | `logging.INFO` | Уровень логирования (`"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`) |
| `log_file` | `str` или `None` | `None` | Путь к файлу. При `None` и `docker_mode=False` — `"logs/app.log"` |
| `docker_mode` | `bool` или `None` | `None` | `True` = только stdout, `False` = файл, `None` = автоопределение по переменной `DOCKER_ENV` |
| `fmt` | `str` или `None` | `None` | Формат логов. При `None` — стандартный формат |

#### Стандартный формат
```
'%(asctime)s | %(name)s | %(levelname)-8s | %(message)s'
```

#### Пример вывода
```
2025-03-30 15:30:45 | MY_SERVICE | INFO     | Сообщение
2025-03-30 15:30:46 | MY_SERVICE | ERROR    | Ошибка
```

## Режимы работы

### Локальная разработка
```bash
# Без DOCKER_ENV
python main.py  # пишет в файл + дублирует в консоль (только сообщения)
```

### Docker/production
```bash
DOCKER_ENV=true python main.py  # только stdout, Docker сам собирает логи
```

### Принудительное указание режима
```python
# Только stdout
logger = get_logger("APP", docker_mode=True)

# Только файл
logger = get_logger("APP", docker_mode=False, log_file="app.log")
```

## Примеры

### Приложение с несколькими модулями

```python
# main.py
from logger_utils import get_logger

logger = get_logger("MAIN", level="DEBUG")

def main():
    logger.info("Application started")
    # ...
```

```python
# module.py
import logging  # можно использовать стандартный logging после настройки
logger = logging.getLogger(__name__)

def do_something():
    logger.debug("Doing something")
```

### Использование с конфигом проекта

```python
# shared/logging.py
from logger_utils import get_logger
from shared.config import config

def setup_logger(name: str):
    return get_logger(
        name=name,
        level=config.LOGGING_LEVEL,
        log_file=config.LOG_PATH / "app.log",
        docker_mode=config.DOCKER_ENV
    )
```

```python
# w_toxicity_filter/app/main.py
from shared.logging import setup_logger

logger = setup_logger("W_TOXICITY_FILTER")

# или сразу
logger = get_logger("W_TOXICITY_FILTER", level="INFO")
```

## Преимущества подхода

- **Нет глобального состояния** — каждый логер создается явно
- **Не зависит от конфигов проекта** — все параметры передаются напрямую
- **Работает везде одинаково** — в разработке, в production, в тестах
- **Простота использования** — одна функция для всех случаев
- **Совместимость со стандартным `logging`** — можно использовать `logging.getLogger()` после настройки

## Зависимости

- `concurrent-log-handler>=0.9.20`

## Лицензия

MIT