"""Ендпоінти зв'язків: 1:N (виробник/категорія -> інструменти) і N:M (музикант <-> інструмент)."""

from typing import Any

from fastapi import APIRouter, status

from lab4.domain import Instrument, MusicianInstrumentIn
from lab4.storage.base import LinkRepository, Repository


def build_relations_router(
    instruments: Repository,
    manufacturers: Repository,
    categories: Repository,
    links: LinkRepository,
) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["relations"])

    @router.get("/manufacturers/{item_id}/instruments", response_model=list[Instrument])
    def by_manufacturer(item_id: int) -> Any:
        manufacturers.get(item_id)  # 404, якщо виробника немає
        return instruments.list(200, 0, {"manufacturer_id": item_id})

    @router.get("/categories/{item_id}/instruments", response_model=list[Instrument])
    def by_category(item_id: int) -> Any:
        categories.get(item_id)
        return instruments.list(200, 0, {"category_id": item_id})

    @router.get("/musicians/{musician_id}/instruments")
    def musician_instruments(musician_id: int) -> list[dict[str, Any]]:
        return links.list_for(musician_id)

    @router.post(
        "/musicians/{musician_id}/instruments/{instrument_id}",
        status_code=status.HTTP_201_CREATED,
    )
    def link(musician_id: int, instrument_id: int, body: MusicianInstrumentIn) -> dict[str, Any]:
        return links.link(musician_id, instrument_id, body.model_dump())

    @router.delete(
        "/musicians/{musician_id}/instruments/{instrument_id}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    def unlink(musician_id: int, instrument_id: int) -> None:
        links.unlink(musician_id, instrument_id)

    return router
