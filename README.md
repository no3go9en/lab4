# ЛР4 · Data Persistence & Web Interfaces — «Музичний інструмент»

REST API на **FastAPI + PostgreSQL (psycopg 3)** для предметної області «Музичний інструмент».

## Сутності та зв'язки
| Таблиця | Опис | Зв'язок |
|---|---|---|
| `categories` | категорія інструмента | 1:N → instruments |
| `manufacturers` | виробник | 1:N → instruments |
| `instruments` | інструмент (серійний номер, ціна, рік) | N:1 → categories, N:1 → manufacturers |
| `musicians` | музикант (ПІБ, email, телефон) | N:M ↔ instruments |
| `musician_instruments` | таблиця зв'язку N:M | — |

ERD: `docs/erd.png`, C4 Code: `docs/c4_code.png`.

## Запуск
```bash
docker compose up -d              # PostgreSQL 18 на localhost:5432
uv sync
uv run lab4-init-db               # CREATE TABLE + 108 тестових записів (SQL з Python)
uv run uvicorn lab4.main:app --reload
```
**Веб-інтерфейс: http://localhost:8000/** (таблиці, додавання/редагування/видалення, фільтри, зв'язки музикант ↔ інструмент).
Swagger UI: http://localhost:8000/docs · демонстрація: `./demo.sh` (вивід — `docs/demo_output.txt`).

## REST API
| Метод | URL | Дія |
|---|---|---|
| GET | `/api/{resource}?limit=&offset=` | список (`categories`, `manufacturers`, `instruments`, `musicians`) |
| GET | `/api/{resource}/{id}` | окремий запис |
| POST | `/api/{resource}` | створення (201 + Location) |
| PUT | `/api/{resource}/{id}` | оновлення |
| DELETE | `/api/{resource}/{id}` | видалення (204) |
| GET | `/api/manufacturers/{id}/instruments`, `/api/categories/{id}/instruments` | 1:N |
| GET/POST/DELETE | `/api/musicians/{id}/instruments[/{instrument_id}]` | N:M |

Фільтри: `/api/instruments?category_id=1&manufacturer_id=2`, `/api/manufacturers?country=США`.

## Regex-валідація (`src/lab4/domain.py`)
- email — `^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$`
- телефон — `^\+380\d{9}$` (пробіли прибираються)
- серійний номер — `^[A-Z]{2,4}-\d{4,8}$` (напр. `YMH-102938`, автоматично у верхній регістр)
- назви / ПІБ, URL сайту виробника

Невалідні дані → **422**, неіснуючий запис → **404**, порушення UNIQUE/FK → **409**.

## Принцип відкритості/закритості
- Роутери залежать лише від протоколу `Repository` (`storage/base.py`). Нове сховище
  (див. `InMemoryRepository`) додається новим класом, без змін у роутерах.
- Новий ресурс = новий `ResourceSpec` у `resources.py`; CRUD генерується `build_crud_router`.

## Якість коду
`uv run ruff check . && uv run ruff format --check . && uv run mypy .` — те саме запускає
`.github/workflows/linter.yml` на GitHub Actions.

## Структура
```
lab04/
├── .github/workflows/linter.yml
├── docker-compose.yaml
├── pyproject.toml / uv.lock
├── demo.sh
├── docs/  erd.mmd/png, c4_code.mmd/png, demo_output.txt, lint_output.txt
└── src/lab4/
    ├── main.py          # збирання FastAPI-застосунку
    ├── static/index.html # веб-інтерфейс (HTML + JS, працює через REST API)
    ├── domain.py        # доменні класи + regex
    ├── resources.py     # реєстр ресурсів (ResourceSpec)
    ├── schema.sql       # DDL
    ├── init_db.py       # ініціалізація таблиць і даних з Python
    ├── api/   crud.py, relations.py
    └── storage/ base.py, postgres.py, memory.py
```
