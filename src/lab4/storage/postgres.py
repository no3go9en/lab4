"""Реалізація сховища на PostgreSQL (psycopg 3).

Усі значення передаються лише як параметри (%s), а імена таблиць/колонок —
через psycopg.sql.Identifier, тож SQL-ін'єкція тут неможлива.
"""

import builtins
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import psycopg
from psycopg import errors, sql
from psycopg.rows import dict_row

from lab4.storage.base import ConflictError, NotFoundError, ResourceSpec, Row


@contextmanager
def connect(dsn: str) -> Iterator[psycopg.Connection[Row]]:
    try:
        with psycopg.connect(dsn, row_factory=dict_row) as conn:
            yield conn
    except (errors.UniqueViolation, errors.ForeignKeyViolation, errors.CheckViolation) as e:
        raise ConflictError(e.diag.message_detail or e.diag.message_primary or str(e)) from e


class PostgresRepository:
    def __init__(self, spec: ResourceSpec, dsn: str) -> None:
        self.spec = spec
        self.dsn = dsn
        self._table = sql.Identifier(spec.table)

    def list(self, limit: int, offset: int, filters: Row | None = None) -> list[Row]:
        where, params = self._where(filters or {})
        query = sql.SQL("SELECT * FROM {} {} ORDER BY id LIMIT %s OFFSET %s").format(
            self._table, where
        )
        with connect(self.dsn) as conn:
            return conn.execute(query, [*params, limit, offset]).fetchall()

    def get(self, item_id: int) -> Row:
        query = sql.SQL("SELECT * FROM {} WHERE id = %s").format(self._table)
        with connect(self.dsn) as conn:
            row = conn.execute(query, (item_id,)).fetchone()
        if row is None:
            raise NotFoundError(f"{self.spec.name}/{item_id} не існує")
        return row

    def create(self, data: Row) -> Row:
        cols = [c for c in self.spec.columns if c in data]
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING *").format(
            self._table,
            sql.SQL(", ").join(map(sql.Identifier, cols)),
            sql.SQL(", ").join(sql.Placeholder() * len(cols)),
        )
        with connect(self.dsn) as conn:
            row = conn.execute(query, [data[c] for c in cols]).fetchone()
        assert row is not None  # noqa: S101 — RETURNING завжди повертає рядок
        return row

    def update(self, item_id: int, data: Row) -> Row:
        cols = [c for c in self.spec.columns if c in data]
        query = sql.SQL("UPDATE {} SET {} WHERE id = %s RETURNING *").format(
            self._table,
            sql.SQL(", ").join(sql.SQL("{} = %s").format(sql.Identifier(c)) for c in cols),
        )
        with connect(self.dsn) as conn:
            row = conn.execute(query, [*(data[c] for c in cols), item_id]).fetchone()
        if row is None:
            raise NotFoundError(f"{self.spec.name}/{item_id} не існує")
        return row

    def delete(self, item_id: int) -> None:
        query = sql.SQL("DELETE FROM {} WHERE id = %s").format(self._table)
        with connect(self.dsn) as conn:
            if conn.execute(query, (item_id,)).rowcount == 0:
                raise NotFoundError(f"{self.spec.name}/{item_id} не існує")

    def count(self) -> int:
        query = sql.SQL("SELECT count(*) AS n FROM {}").format(self._table)
        with connect(self.dsn) as conn:
            row = conn.execute(query).fetchone()
        return int(row["n"]) if row else 0

    def _where(self, filters: Row) -> tuple[sql.Composable, builtins.list[Any]]:
        used = {k: v for k, v in filters.items() if k in self.spec.filters and v is not None}
        if not used:
            return sql.SQL(""), []
        cond = sql.SQL(" AND ").join(sql.SQL("{} = %s").format(sql.Identifier(k)) for k in used)
        return sql.SQL("WHERE ") + cond, list(used.values())


class PostgresMusicianInstruments:
    """N:M musicians <-> instruments через таблицю musician_instruments."""

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    def list_for(self, left_id: int) -> list[Row]:
        with connect(self.dsn) as conn:
            if conn.execute("SELECT 1 FROM musicians WHERE id = %s", (left_id,)).fetchone() is None:
                raise NotFoundError(f"musicians/{left_id} не існує")
            return conn.execute(
                "SELECT i.*, mi.since_year FROM musician_instruments mi"
                " JOIN instruments i ON i.id = mi.instrument_id"
                " WHERE mi.musician_id = %s ORDER BY i.id",
                (left_id,),
            ).fetchall()

    def link(self, left_id: int, right_id: int, extra: Row) -> Row:
        with connect(self.dsn) as conn:
            row = conn.execute(
                "INSERT INTO musician_instruments (musician_id, instrument_id, since_year)"
                " VALUES (%s, %s, %s) RETURNING *",
                (left_id, right_id, extra.get("since_year")),
            ).fetchone()
        assert row is not None  # noqa: S101
        return row

    def unlink(self, left_id: int, right_id: int) -> None:
        with connect(self.dsn) as conn:
            cur = conn.execute(
                "DELETE FROM musician_instruments WHERE musician_id = %s AND instrument_id = %s",
                (left_id, right_id),
            )
            if cur.rowcount == 0:
                raise NotFoundError("такого зв'язку немає")
