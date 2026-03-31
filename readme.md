# logger-utils

Утилита для настройки логирования в Python-приложениях с поддержкой многопроцессной записи, Docker-окружения и автоматической подстановки имени процесса.

## Возможности

- **Многопроцессная ротация файлов** — через `ConcurrentRotatingFileHandler` (без гонок)
- **Docker-режим** — автоматическое переключение на stdout при `DOCKER_ENV=true`
- **Автоматическая подстановка имени процесса** — во все логи, включая shared модули
- **Однократная настройка** — первый вызов `get_logger()` настраивает корневой логер
- **Одна функция** — всё в одном месте

## Установка

```bash
pip install git+https://github.com/sidorov-works/logger_utils@v0.3.1
```

## Использование

### 1. В точке входа процесса (воркер, CLI-скрипт, main)

```python
from logger_utils import get_logger
from pathlib import Path

# Первый вызов в процессе - настраивает корневой логер и подставляет process_name
logger = get_logger(
    name="MY_WORKER",                   # имя логера
    process_name="MY_WORKER",           # имя процесса (будет во всех логах)
    level="INFO",                       # уровень логирования
    log_file=str(Path("logs") / "app.log"),
    docker_mode=False,                  # или None для автоопределения по DOCKER_ENV
    fmt='%(asctime)s | %(process_name)-15s | %(name)-30s | %(levelname)-8s | %(message)s'
)

logger.info("Worker started")
logger.error("Something went wrong", exc_info=True)
```

### 2. В shared модулях (библиотеках, утилитах) — без изменений

```python
import logging

logger = logging.getLogger(__name__)   # стандартный подход

def do_something():
    logger.info("Doing something")     # process_name подставится автоматически
```

### 3. В других модулях того же процесса

```python
from logger_utils import get_logger

logger = get_logger("ANOTHER_MODULE")  # вернет логер с указанным именем
logger.info("Some message")            # process_name уже есть в корневом логере
```

## Параметры get_logger

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `name` | `str` или `None` | `None` | Имя логера. Если `None`, возвращает корневой логер |
| `process_name` | `str` или `None` | `None` | Имя процесса. Если указан, подставляется в поле `process_name` всех логов |
| `level` | `int` или `str` | `logging.INFO` | Уровень логирования (только при первом вызове) |
| `log_file` | `str` или `None` | `None` | Путь к файлу. При `None` и не Docker — `"logs/app.log"` |
| `docker_mode` | `bool` или `None` | `None` | `True` = только stdout, `False` = файл, `None` = авто по `DOCKER_ENV` |
| `fmt` | `str` | `'%(asctime)s \| %(process_name)-15s \| %(name)-30s \| %(levelname)-8s \| %(message)s'` | Формат логов |

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
2025-03-31 10:00:00 | W_ESCALATION_ROUTER | W_ESCALATION_ROUTER            | INFO     | Worker started
2025-03-31 10:00:01 | W_ESCALATION_ROUTER | shared.queue_client            | INFO     | Pushing item
2025-03-31 10:00:02 | W_ESCALATION_ROUTER | shared.database                | DEBUG    | Connecting to DB
2025-03-31 10:00:03 | W_ESCALATION_ROUTER | W_ESCALATION_ROUTER            | ERROR    | Something went wrong
```

## Как это работает

1. **Первый вызов** `get_logger()` в процессе настраивает корневой логер (добавляет handlers)
2. Если указан `process_name`, методы корневого логера оборачиваются и подставляют `process_name` в `extra` каждого сообщения
3. **Все последующие вызовы** просто возвращают логер с указанным именем
4. **Shared модули** используют стандартный `logging.getLogger(__name__)`
5. У логеров из shared модулей нет своих handlers, поэтому они прокидывают события корневому логеру
6. Корневой логер имеет handlers и обернутые методы → логи выводятся с `process_name`

## Преимущества

- **Одна функция** — не нужно думать, где вызывать `configure_root` и `wrap_logger`
- **Shared модули не меняются** — используют стандартный `logging.getLogger(__name__)`
- **Имя процесса во всех логах** — включая логи из shared модулей
- **Нет глобальных переменных в коде проекта** — всё состояние скрыто внутри библиотеки
- **Поддержка многопроцессности** — каждый процесс настраивает свой корневой логер независимо

## Зависимости

- `concurrent-log-handler>=0.9.20`

## Лицензия

MIT