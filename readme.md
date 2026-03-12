# logger-utils

Утилита для настройки логирования в Python-приложениях с поддержкой многопроцессной записи и Docker-окружения.

## Возможности

- **Многопроцессная ротация файлов** — через `ConcurrentRotatingFileHandler` (без гонок)
- **Docker-режим** — автоматическое переключение на stdout при `DOCKER_ENV=true`
- **Единая конфигурация** — настройка корневого логера для всего приложения
- **Автоматическое имя модуля** — через `%(name)s` в форматтере

## Установка

```bash
pip install git+https://github.com/your-org/logger-utils.git@v0.1.7
```

## Использование

### 1. Настройка при запуске приложения

```python
from logger_utils import configure_root, get_logger
from pathlib import Path

# Один раз при старте
configure_root(
    level="INFO",
    log_file=str(Path("logs") / "app.log"),
    fmt='%(asctime)s | %(name)s | %(levelname)-8s | %(message)s'
)

# Получение логера
logger = get_logger(__name__)
```

### 2. В модулях проекта

```python
# shared/catalog_api.py
import logging
logger = logging.getLogger(__name__)  # имя = "shared.catalog_api"

logger.info("Сообщение")  # попадёт в настроенный файл
```

### 3. В Docker-окружении

```yaml
# docker-compose.yml
services:
  app:
    environment:
      - DOCKER_ENV=true  # переключает на stdout
```

Без этой переменной логер пишет в файл (локальная разработка).

## Параметры configure_root

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `level` | `int` или `str` | `logging.INFO` | Уровень логирования |
| `log_file` | `str` или `None` | `"logs/app.log"` | Путь к файлу (вне Docker) |
| `docker_mode` | `bool` или `None` | `None` | `True` = только stdout, `False` = файл, `None` = авто по `DOCKER_ENV` |
| `fmt` | `str` | `'%(asctime)s \| %(name)s \| %(levelname)-8s \| %(message)s'` | Формат логов |

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