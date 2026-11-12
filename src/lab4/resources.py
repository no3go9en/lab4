"""Реєстр REST-ресурсів. Щоб додати новий ресурс — додай ResourceSpec у RESOURCES."""

from lab4.domain import (
    Category,
    CategoryIn,
    Instrument,
    InstrumentIn,
    Manufacturer,
    ManufacturerIn,
    Musician,
    MusicianIn,
)
from lab4.storage.base import ResourceSpec

CATEGORIES = ResourceSpec("categories", "categories", CategoryIn, Category)
MANUFACTURERS = ResourceSpec(
    "manufacturers", "manufacturers", ManufacturerIn, Manufacturer, filters=("country",)
)
INSTRUMENTS = ResourceSpec(
    "instruments",
    "instruments",
    InstrumentIn,
    Instrument,
    filters=("category_id", "manufacturer_id"),
)
MUSICIANS = ResourceSpec("musicians", "musicians", MusicianIn, Musician)

RESOURCES: tuple[ResourceSpec, ...] = (CATEGORIES, MANUFACTURERS, INSTRUMENTS, MUSICIANS)
