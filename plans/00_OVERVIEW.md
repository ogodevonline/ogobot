# S.E.A.C. (Self-Evolving AI Core) — Архитектурный План

## Обзор

Это главный документ архитектуры. Остальные документы организованы по темам:

- [`01_PROJECT_STRUCTURE.md`](01_PROJECT_STRUCTURE.md) — структура файлов и слои Clean Architecture
- [`02_DATABASE_SCHEMA.md`](02_DATABASE_SCHEMA.md) — модели SQLite и схема БД
- [`03_STATE_MODEL.md`](03_STATE_MODEL.md) — модель State для Pydantic Graph
- [`04_DYNAMIC_IMPORT.md`](04_DYNAMIC_IMPORT.md) — механизм динамического импорта инструментов
- [`05_GRAPH_FLOW.md`](05_GRAPH_FLOW.md) — диаграмма потока данных через граф

## Ключевые Принципы

1. **Clean Architecture** — зависимости текут внутрь (entrypoints → application → domain)
2. **No-Chaos Config** — максимум 150 строк в файле, функции ≤ 30 строк, вложенность ≤ 3
3. **Type Safety** — 100% type hints, Pydantic для валидации
4. **Безопасность** — sandboxing, таймауты, проверка AST для динамического кода
5. **Восстанавливаемость** — checkpoints в БД для восстановления после падения

## Стек Технологий

| Компонент | Технология |
|-----------|-----------|
| Логика агента | Pydantic AI + Pydantic Graph |
| Интерфейс | aiogram (Telegram Bot API) |
| БД | SQLite (SQLAlchemy ORM) |
| Планирование | APScheduler |
| Мониторинг | Logfire + structlog |
| Линтинг | ruff + pyright |
| Логирование | loguru |
| Управление зависимостями | uv |

## Фазы Реализации

1. **Phase 1** — Базовый backbone (граф, БД, логирование)
2. **Phase 2** — Интеграция Telegram (aiogram)
3. **Phase 3** — Динамический импорт инструментов
4. **Phase 4** — Human-in-the-Loop (подтверждение действий)
5. **Phase 5** — Scheduling (APScheduler)
6. **Phase 6** — Мониторинг (Logfire)

---

**Начните с изучения [`01_PROJECT_STRUCTURE.md`](01_PROJECT_STRUCTURE.md)**
