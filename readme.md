# logger-utils

Кастомный логгер с поддержкой многопроцессной записи в файл и Docker-окружения.

## Возможности

- **Многопроцессная ротация файлов** — через `ConcurrentRotatingFileHandler` (без гонок)
- **Docker-режим** — автоматическое переключение на stdout при `DOCKER_ENV=true`
- **Единая конфигурация** — настройка корневого логера для всего приложения
- **Имена процессов** — декоратор `wrap_logger_methods` для добавления `process_name` в логи

## Установка

```bash
pip install git+https://github.com/sidorov-works/logger_utils.git@v0.1.6
```

## Использование

### 1. Настройка при запуске приложения

```python
from logger_utils import configure_root, get_logger, wrap_logger_methods

# ОДИН РАЗ при старте приложения
configure_root(
    level="INFO",                    # уровень логирования
    log_file="logs/myapp.log",       # путь к файлу (игнорируется в Docker)
    docker_mode=None,                 # None = автоопределение по DOCKER_ENV
    fmt='%(asctime)s | %(levelname)-8s | %(process_name)-12s | %(message)s'
)
```

### 2. Получение логера в модулях

```python
# В любом модуле проекта
from logger_utils import get_logger

logger = get_logger(__name__)
logger.info("Сервис запущен")  # попадёт в настроенный файл/stdout
```

### 3. Добавление имени процесса (для воркеров)

```python
from logger_utils import wrap_logger_methods

worker_logger = wrap_logger_methods(logger, "worker-1")
worker_logger.info("Обработка задачи")  # в логах появится process_name=worker-1
```

### 4. Логеры из других пакетов

```python
from retryable_http_client import RetryableHTTPClient

# Этот клиент использует стандартный logging.getLogger()
# Он автоматически получит все настройки от корневого логера!
client = RetryableHTTPClient()
```

## Параметры configure_root

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `level` | `int` или `str` | `logging.INFO` | Уровень логирования |
| `log_file` | `str` или `None` | `"logs/app.log"` | Путь к файлу (вне Docker) |
| `docker_mode` | `bool` или `None` | `None` | `True` = только stdout, `False` = файл, `None` = авто по `DOCKER_ENV` |
| `fmt` | `str` | `'%(asctime)s | %(levelname)-8s | %(process_name)-12s | %(message)s'` | Формат логов |

## Режимы работы

### Локальная разработка
```bash
# Без DOCKER_ENV
python main.py  # пишет в файл + дублирует в консоль
```

### Docker/production
```bash
DOCKER_ENV=true python main.py  # только stdout, Docker сам собирает логи
```

## Зависимости

- `concurrent-log-handler>=0.9.20`

## Версионирование

Семантическое версионирование. Теги: `v0.1.0`, `v0.1.1` и т.д.

## Лицензия

MIT