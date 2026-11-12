"""Фабрика CRUD-роутерів: один і той самий код обслуговує всі ресурси (OCP)."""

from typing import Annotated, Any, cast

from fastapi import APIRouter, Query, Request, Response, status
from pydantic import BaseModel

from lab4.storage.base import Repository


def build_crud_router(repo: Repository) -> APIRouter:
    spec = repo.spec
    router = APIRouter(prefix=f"/api/{spec.name}", tags=[spec.name])
    In, Out = spec.in_model, spec.out_model  # noqa: N806

    @router.get(
        "",
        response_model=list[Out],  # type: ignore[valid-type]
        summary=f"Список {spec.name}",
    )
    def list_items(
        request: Request,
        limit: Annotated[int, Query(ge=1, le=200)] = 50,
        offset: Annotated[int, Query(ge=0)] = 0,
    ) -> Any:
        raw = {k: request.query_params.get(k) for k in spec.filters}
        filters = {k: int(v) if v and v.isdigit() else v for k, v in raw.items()}
        return repo.list(limit, offset, filters)

    @router.get("/{item_id}", response_model=Out, summary="Окремий запис")
    def get_item(item_id: int) -> Any:
        return repo.get(item_id)

    @router.post("", response_model=Out, status_code=status.HTTP_201_CREATED, summary="Створити")
    def create_item(body: In, response: Response) -> Any:  # type: ignore[valid-type]
        row = repo.create(cast(BaseModel, body).model_dump())
        response.headers["Location"] = f"/api/{spec.name}/{row['id']}"
        return row

    @router.put("/{item_id}", response_model=Out, summary="Оновити")
    def update_item(item_id: int, body: In) -> Any:  # type: ignore[valid-type]
        return repo.update(item_id, cast(BaseModel, body).model_dump())

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Видалити")
    def delete_item(item_id: int) -> None:
        repo.delete(item_id)

    return router
