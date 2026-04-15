# 1. Структура Проекта и Clean Architecture

## Иерархия Слоев

```
ogobot/
├── src/
│   ├── domain/                    # Бизнес-логика (NO external deps)
│   │   ├── __init__.py
│   │   ├── entities.py            # Доменные сущности (State, Task, Tool)
│   │   ├── value_objects.py       # Value Objects (TaskId, ToolId)
│   │   └── exceptions.py          # Доменные исключения
│   │
│   ├── application/               # Бизнес-правила (зависит только от domain)
│   │   ├── __init__.py
│   │   ├── repositories.py        # Repository Pattern интерфейсы
│   │   ├── unit_of_work.py        # Unit of Work интерфейс
│   │   ├── services.py            # Application Services (≤30 строк)
│   │   └── dto.py                 # Data Transfer Objects
│   │
│   ├── infrastructure/            # Реализация (зависит от application + domain)
│   │   ├── __init__.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── models.py          # SQLAlchemy ORM модели
│   │   │   ├── repositories.py    # Реализация Repository
│   │   │   ├── unit_of_work.py    # Реализация Unit of Work
│   │   │   └── session.py         # Session factory
│   │   ├── logging/
│   │   │   ├── __init__.py
│   │   │   └── config.py          # loguru + structlog конфиг
│   │   └── code_executor/
│   │       ├── __init__.py
│   │       ├── sandbox.py         # Sandboxing логика
│   │       └── validator.py       # AST-based валидация
│   │
│   ├── entrypoints/               # Точки входа (зависит от всех слоев)
│   │   ├── __init__.py
│   │   ├── telegram_bot.py        # aiogram интеграция
│   │   ├── scheduler.py           # APScheduler интеграция
│   │   └── graph.py               # Pydantic Graph инициализация
│   │
│   └── tools/                     # Динамически создаваемые инструменты
│       ├── __init__.py
│       ├── registry.py            # Реестр инструментов
│       └── [generated_tools]/     # Сгенерированные инструменты
│
├── tests/
│   ├── unit/                      # Unit тесты (domain + application)
│   ├── integration/               # Integration тесты (infrastructure)
│   └── e2e/                       # E2E тесты (entrypoints)
│
├── manifests/                     # YAML-описания прав доступа
│   └── skills.yaml
│
├── plans/                         # Архитектурная документация
│   ├── 00_OVERVIEW.md
│   ├── 01_PROJECT_STRUCTURE.md
│   ├── 02_DATABASE_SCHEMA.md
│   ├── 03_STATE_MODEL.md
│   ├── 04_DYNAMIC_IMPORT.md
│   └── 05_GRAPH_FLOW.md
│
├── .env.example
├── .env                           # (в .gitignore)
├── pyproject.toml
├── uv.lock
└── .gitignore
```

## Правила Слоев

| Слой | Может импортировать | Не может импортировать |
|------|-------------------|----------------------|
| **domain** | Ничего (только stdlib) | application, infrastructure, entrypoints |
| **application** | domain | infrastructure, entrypoints |
| **infrastructure** | domain, application | entrypoints |
| **entrypoints** | Все | Ничего (точка входа) |

## Ограничения No-Chaos

- **Файл** ≤ 150 строк
- **Функция** ≤ 30 строк
- **Вложенность** ≤ 3 уровня
- **Type hints** 100%
- **Импорты** в начале файла, отсортированы

---

**Далее:** [`02_DATABASE_SCHEMA.md`](02_DATABASE_SCHEMA.md)
