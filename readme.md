# logger-utils

Утилита для настройки логирования в Python-приложениях с поддержкой многопроцессной записи и Docker-окружения.

## Возможности

- **Многопроцессная ротация файлов** — через `ConcurrentRotatingFileHandler` (без гонок)
- **Docker-режим** — автоматическое переключение на stdout при `DOCKER_ENV=true`
- **Однократная настройка** — первый вызов `get_logger()` настраивает корневой логер
- **Простота** — одна функция для всего

## Установка

```bash
pip install git+https://github.com/sidorov-works/logger_utils@v0.3.0
```

## Использование

### 1. В точке входа процесса (воркер, CLI-скрипт, main)

```python
from logger_utils import get_logger
from pathlib import Path

# Первый вызов в процессе - настраивает корневой логер
logger = get_logger(
    name="MY_WORKER",                   # имя логера
    level="INFO",                       # уровень логирования
    log_file=str(Path("logs") / "app.log"),
    docker_mode=False,                  # или None для автоопределения по DOCKER_ENV
    fmt='%(asctime)s | %(name)-30s | %(levelname)-8s | %(message)s'
)

logger.info("Worker started")
logger.error("Something went wrong", exc_info=True)
```

### 2. В shared модулях (библиотеках, утилитах)

```python
import logging

logger = logging.getLogger(__name__)   # стандартный подход

def do_something():
    logger.info("Doing something")     # логи пойдут в тот же файл
```

### 3. В других модулях того же процесса

```python
from logger_utils import get_logger

logger = get_logger("ANOTHER_MODULE")  # вернет логер с указанным именем
logger.info("Some message")
```

## Параметры get_logger

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `name` | `str` или `None` | `None` | Имя логера. Если `None`, возвращает корневой логер |
| `level` | `int` или `str` | `logging.INFO` | Уровень логирования (только при первом вызове) |
| `log_file` | `str` или `None` | `None` | Путь к файлу. При `None` и не Docker — `"logs/app.log"` |
| `docker_mode` | `bool` или `None` | `None` | `True` = только stdout, `False` = файл, `None` = авто по `DOCKER_ENV` |
| `fmt` | `str` | `'%(asctime)s \| %(name)-30s \| %(levelname)-8s \| %(message)s'` | Формат логов |

## Режимы работы

### Локальная разработка

```bash
python my_worker.py
# Пишет в файл logs/app.log + дублирует в консоль (только сообщения без формата)
```

### Docker/production

```bash
DOCKER_ENV=true python my_worker.py
# Пишет только в stdout, Docker сам собирает логи
```

### Принудительное указание режима

```python
# Только stdout
logger = get_logger("WORKER", docker_mode=True)

# Только файл с кастомным путем
logger = get_logger("WORKER", docker_mode=False, log_file="/var/log/app.log")
```

## Пример вывода логов

```
2025-03-31 10:00:00 | W_ESCALATION_ROUTER            | INFO     | Worker started
2025-03-31 10:00:01 | shared.queue_client            | INFO     | Pushing item
2025-03-31 10:00:02 | shared.database                | DEBUG    | Connecting to DB
2025-03-31 10:00:03 | W_ESCALATION_ROUTER            | ERROR    | Something went wrong
```

## Как это работает

1. **Первый вызов** `get_logger()` в процессе настраивает корневой логер (добавляет handlers)
2. **Все последующие вызовы** просто возвращают логер с указанным именем
3. **Shared модули** используют стандартный `logging.getLogger(__name__)`
4. У логеров из shared модулей нет своих handlers, поэтому они прокидывают события корневому логеру
5. Корневой логер имеет handlers → логи выводятся

## Преимущества

- **Одна функция** — не нужно думать, где вызывать `configure_root`
- **Стандартный подход в shared модулях** — используется `logging.getLogger(__name__)`
- **Нет глобальных переменных в коде проекта** — всё состояние скрыто внутри библиотеки
- **Поддержка многопроцессности** — каждый процесс настраивает свой корневой логер независимо
- **Нет костылей** — только стандартные механизмы `logging`

## Зависимости

- `concurrent-log-handler>=0.9.20`

## Лицензия

MIT