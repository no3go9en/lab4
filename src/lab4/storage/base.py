"""Абстракції сховища.

Принцип відкритості/закритості (OCP): API працює лише з протоколом `Repository`.
Щоб додати новий тип сховища (Mongo, Redis, файл...), достатньо написати новий клас,
що реалізує протокол, — код роутерів і доменних моделей не змінюється.
"""

from dataclasses import dataclass, field
from typing import Any, Protocol

from pydantic import BaseModel

Row = dict[str, Any]


class NotFoundError(Exception):
    """Запис не знайдено (-> HTTP 404)."""


class ConflictError(Exception):
    """Порушення унікальності / зовнішнього ключа (-> HTTP 409)."""


@dataclass(frozen=True)
class ResourceSpec:
    """Опис REST-ресурсу. Новий ресурс = новий ResourceSpec, без зміни існуючого коду."""

    name: str  # сегмент URL, напр. "instruments"
    table: str  # таблиця / колекція
    in_model: type[BaseModel]
    out_model: type[BaseModel]
    filters: tuple[str, ...] = field(default=())  # поля, за якими дозволено фільтрувати

    @property
    def columns(self) -> list[str]:
        return list(self.in_model.model_fields)


class Repository(Protocol):
    spec: ResourceSpec

    def list(self, limit: int, offset: int, filters: Row | None = None) -> list[Row]: ...
    def get(self, item_id: int) -> Row: ...
    def create(self, data: Row) -> Row: ...
    def update(self, item_id: int, data: Row) -> Row: ...
    def delete(self, item_id: int) -> None: ...
    def count(self) -> int: ...


class LinkRepository(Protocol):
    """Зв'язок N:M (музикант <-> інструмент)."""

    def list_for(self, left_id: int) -> list[Row]: ...
    def link(self, left_id: int, right_id: int, extra: Row) -> Row: ...
    def unlink(self, left_id: int, right_id: int) -> None: ...
