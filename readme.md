# logger-utils

Кастомный логгер для Python-приложений с поддержкой многопроцессной записи и Docker-окружения.

## Возможности

- **Многопроцессная запись** — потокобезопасная ротация файлов через `ConcurrentRotatingFileHandler`
- **Docker-режим** — автоматическое переключение на stdout при `DOCKER_ENV=true`
- **Уровни логирования** — настраиваются через параметры
- **Имена процессов** — автоматическая подстановка через декоратор `wrap_logger_methods`
- **Готовый инстанс** — можно импортировать и сразу использовать

## Установка

```bash
pip install git+https://github.com/sidorov-works/logger_utils.git@v0.1.2
```

## Быстрый старт

```python
from logger_utils import logger, wrap_logger_methods

# Использование готового логера
logger.info("Сервис запущен")

# Создание логера для воркера
worker_logger = wrap_logger_methods(logger, "worker-1")
worker_logger.info("Обработка задачи")  # в логах появится process_name=worker-1
```

## API

### `get_logger(name: Optional[str] = None, level: Union[int, str] = logging.DEBUG) -> logging.Logger`

Создает логер с автоматическим выбором режима:
- `DOCKER_ENV=true` — только stdout
- иначе — файл + консоль

### `logger` — готовый инстанс для импорта

### `wrap_logger_methods(logger, worker_name: str) -> logging.Logger`

Добавляет `process_name` в каждую запись лога.

## Конфигурация через окружение

- `DOCKER_ENV=true` — переключает в Docker-режим (stdout)

## Зависимости

- `concurrent-log-handler>=0.9.20`

## Разработка

```bash
git clone https://github.com/your-org/logger-utils.git
cd logger-utils
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -e .
```

## Лицензия

MIT