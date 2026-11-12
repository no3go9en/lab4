"""Доменні класи та regex-валідація вхідних даних (пункт 5.b)."""

import re
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# --- регулярні вирази ---------------------------------------------------------
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^\+380\d{9}$")  # український номер: +380XXXXXXXXX
SERIAL_RE = re.compile(r"^[A-Z]{2,4}-\d{4,8}$")  # напр. YMH-102938
NAME_RE = re.compile(r"^[A-Za-zА-ЩЬЮЯҐЄІЇа-щьюяґєії0-9'’ .&()-]{2,120}$")
URL_RE = re.compile(r"^https?://[\w.-]+\.[a-z]{2,}(/\S*)?$")


def _check(pattern: re.Pattern[str], value: str, what: str) -> str:
    value = value.strip()
    if not pattern.fullmatch(value):
        raise ValueError(f"невірний формат ({what}): {value!r}")
    return value


class _Model(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


# --- Category -----------------------------------------------------------------
class CategoryIn(_Model):
    name: str
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def _name(cls, v: str) -> str:
        return _check(NAME_RE, v, "назва")


class Category(CategoryIn):
    id: int


# --- Manufacturer -------------------------------------------------------------
class ManufacturerIn(_Model):
    name: str
    country: str
    email: str
    website: str | None = None

    @field_validator("name", "country")
    @classmethod
    def _name(cls, v: str) -> str:
        return _check(NAME_RE, v, "назва")

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return _check(EMAIL_RE, v, "email")

    @field_validator("website")
    @classmethod
    def _url(cls, v: str | None) -> str | None:
        return None if v is None else _check(URL_RE, v, "URL")


class Manufacturer(ManufacturerIn):
    id: int


# --- Instrument ---------------------------------------------------------------
class InstrumentIn(_Model):
    serial_number: str
    name: str
    category_id: int = Field(gt=0)
    manufacturer_id: int = Field(gt=0)
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    year_made: int = Field(ge=1600, le=2100)

    @field_validator("serial_number")
    @classmethod
    def _serial(cls, v: str) -> str:
        return _check(SERIAL_RE, v.upper(), "серійний номер")

    @field_validator("name")
    @classmethod
    def _name(cls, v: str) -> str:
        return _check(NAME_RE, v, "назва")


class Instrument(InstrumentIn):
    id: int


# --- Musician -----------------------------------------------------------------
class MusicianIn(_Model):
    full_name: str
    email: str
    phone: str

    @field_validator("full_name")
    @classmethod
    def _name(cls, v: str) -> str:
        return _check(NAME_RE, v, "ПІБ")

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return _check(EMAIL_RE, v, "email")

    @field_validator("phone")
    @classmethod
    def _phone(cls, v: str) -> str:
        return _check(PHONE_RE, v.replace(" ", ""), "телефон")


class Musician(MusicianIn):
    id: int


class MusicianInstrumentIn(_Model):
    since_year: int | None = Field(default=None, ge=1900, le=2100)
