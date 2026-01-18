# DocQA RAG Project

## Описание
DocQA — это проект для работы с RAG (Retrieval-Augmented Generation) системами. Он предоставляет удобный интерфейс для взаимодействия с моделями, эмбеддерами, векторной базой и другими компонентами системы.

## Структура проекта

```
.
├── configs/                  # Конфигурационные файлы
│   ├── embedding.yaml        # Конфигурация моделей эмбеддингов
│   ├── fast_api.yaml         # Конфигурация FastAPI
│   ├── indexer.yaml          # Конфигурация индексатора
│   ├── ollama.yaml           # Конфигурация Ollama
│   ├── qdrant.yaml           # Конфигурация Qdrant
│   └── querier.yaml          # Конфигурация запросов
├── src/
│   ├── helpers/              # Вспомогательные модули
│   │   ├── configs_hub.py     # Хаб конфигураций
│   │   ├── config_manager.py  # Менеджер конфигураций
│   │   ├── health_checks.py   # Проверки здоровья
│   │   ├── models_management.py # Управление моделями
│   │   └── qdrant_management.py # Управление Qdrant
│   ├── logging/              # Логирование
│   │   └── logger.py          # Настройка логирования
│   ├── managers/             # Менеджеры
│   │   └── qdrant.py          # Менеджер Qdrant
│   ├── models/               # Модели
│   │   └── embedding.py       # Модели эмбеддингов
│   ├── processors/           # Процессоры
│   │   └── document.py        # Процессор документов
│   ├── services/             # Сервисы
│   │   └── indexer.py         # Сервис индексации
│   ├── web/                  # Веб-интерфейс
│   │   ├── app.py             # Основное приложение FastAPI
│   │   ├── main.py            # Точка входа
│   │   ├── api/               # API маршруты
│   │   │   ├── router.py      # Основной роутер
│   │   │   └── v1/            # Версия 1 API
│   │   │       ├── router.py  # Роутер версии 1
│   │   │       └── routes/    # Маршруты
│   │   │           ├── documents.py # Маршруты для документов
│   │   │           ├── embedding.py # Маршруты для эмбеддингов
│   │   │           ├── health.py    # Маршруты для проверки здоровья
│   │   │           ├── meta.py      # Маршруты для метаинформации
│   │   │           ├── ollama.py    # Маршруты для Ollama
│   │   │           ├── qdrant.py    # Маршруты для Qdrant
│   │   │           └── query.py    # Маршруты для запросов
│   └── middlewares/          # Middleware
│       └── error_handler.py  # Обработка ошибок
├── tests/                    # Тесты
│   ├── conftest.py           # Фикстуры для тестов
│   └── test_api.py           # Тесты для API
├── .gitignore
├── README.md                 # Документация проекта
├── roadmap.md                # План развития проекта
└── plans/                    # Планы и документация
    └── project_structure_plan.md # План по улучшению структуры проекта
```

## Установка и запуск

### Предварительные требования
- Python 3.8+
- Docker (для запуска Qdrant и Ollama)

### Установка зависимостей

```bash
pip install -r deployment/requirements.txt
```

### Запуск приложения

```bash
uvicorn src.web.main:app --reload
```

### Запуск тестов

```bash
pytest tests/
```

## API Документация

После запуска приложения, документация API будет доступна по следующим адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI: http://localhost:8000/openapi.json

## Основные эндпоинты

### Здоровье системы
- `GET /v1/health` — Проверка здоровья системы

### Метаинформация
- `GET /v1/meta/info` — Получение метаинформации о API

### Документы
- `POST /v1/documents/ingest` — Загрузка документов
- `GET /v1/documents` — Получение списка документов
- `DELETE /v1/documents` — Удаление документов

### Запросы
- `POST /v1/query` — Запрос к RAG системе

### Qdrant
- `GET /v1/qdrant/create_collections` — Создание коллекций в Qdrant

### Ollama
- `GET /v1/ollama/get_models_list` — Получение списка моделей Ollama
- `GET /v1/ollama/check_models` — Проверка наличия моделей Ollama
- `POST /v1/ollama/pull_model` — Загрузка модели Ollama

### Эмбеддинги
- `GET /v1/embedding/check_models` — Проверка наличия моделей эмбеддингов
- `POST /v1/embedding/pull_model` — Загрузка моделей эмбеддингов

## Конфигурация

Конфигурации хранятся в файлах YAML в директории `configs/`. Для загрузки конфигураций используется модуль `src/helpers/config_manager.py`.

## Логирование

Логирование настроено с использованием `loguru`. Логи выводятся в stdout и могут быть сохранены в файл. Уровень логирования и файл логов можно настроить в конфигурации.

## Обработка ошибок

Для обработки ошибок используется middleware `ErrorHandlerMiddleware`, который перехватывает все исключения и возвращает стандартный ответ с ошибкой.

## Тестирование

Тесты написаны с использованием `pytest` и `TestClient` из FastAPI. Тесты покрывают основные эндпоинты API.

### Запуск автотестов

Для запуска автотестов с использованием PyCharm и Docker, следуйте инструкциям в [руководстве по тестированию](docs/testing_guide.md).

### Примеры команд для запуска тестов

```bash
# Запуск всех тестов
pytest tests/

# Запуск конкретного теста
pytest tests/test_api.py::test_health_check -v
```

## Лицензия

MIT License