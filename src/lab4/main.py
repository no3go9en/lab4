"""Збирання застосунку. Запуск: uv run uvicorn lab4.main:app --reload"""

from importlib.resources import files

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from lab4.api.crud import build_crud_router
from lab4.api.relations import build_relations_router
from lab4.resources import CATEGORIES, INSTRUMENTS, MANUFACTURERS, RESOURCES
from lab4.storage import DSN
from lab4.storage.base import ConflictError, NotFoundError, Repository
from lab4.storage.postgres import PostgresMusicianInstruments, PostgresRepository


def create_app(dsn: str = DSN) -> FastAPI:
    app = FastAPI(
        title="ЛР4 · Музичний інструмент",
        description="REST API: категорії, виробники, інструменти, музиканти (PostgreSQL).",
        version="1.0.0",
    )

    # Тип сховища обирається тут і лише тут. Інша реалізація Repository
    # (напр. InMemoryRepository) підставляється без змін у роутерах.
    repos: dict[str, Repository] = {spec.name: PostgresRepository(spec, dsn) for spec in RESOURCES}

    for repo in repos.values():
        app.include_router(build_crud_router(repo))
    app.include_router(
        build_relations_router(
            repos[INSTRUMENTS.name],
            repos[MANUFACTURERS.name],
            repos[CATEGORIES.name],
            PostgresMusicianInstruments(dsn),
        )
    )

    # Веб-інтерфейс: одна HTML-сторінка, яка працює з REST API через fetch()
    index_html = (files("lab4") / "static" / "index.html").read_text(encoding="utf-8")

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def index() -> str:
        return index_html

    @app.exception_handler(NotFoundError)
    def _not_found(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=404)

    @app.exception_handler(ConflictError)
    def _conflict(_: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse({"detail": f"Конфлікт даних: {exc}"}, status_code=409)

    return app


app = create_app()
