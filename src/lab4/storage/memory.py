"""In-memory сховище — приклад розширення без зміни існуючого коду (OCP).

Використовується у unit-тестах замість PostgreSQL.
"""

from itertools import count

from lab4.storage.base import NotFoundError, ResourceSpec, Row


class InMemoryRepository:
    def __init__(self, spec: ResourceSpec) -> None:
        self.spec = spec
        self._rows: dict[int, Row] = {}
        self._ids = count(1)

    def list(self, limit: int, offset: int, filters: Row | None = None) -> list[Row]:
        used = {k: v for k, v in (filters or {}).items() if k in self.spec.filters and v}
        rows = [r for r in self._rows.values() if all(r.get(k) == v for k, v in used.items())]
        return rows[offset : offset + limit]

    def get(self, item_id: int) -> Row:
        if item_id not in self._rows:
            raise NotFoundError(f"{self.spec.name}/{item_id} не існує")
        return self._rows[item_id]

    def create(self, data: Row) -> Row:
        row = {"id": next(self._ids), **data}
        self._rows[row["id"]] = row
        return row

    def update(self, item_id: int, data: Row) -> Row:
        row = self.get(item_id) | data
        self._rows[item_id] = row
        return row

    def delete(self, item_id: int) -> None:
        self.get(item_id)
        del self._rows[item_id]

    def count(self) -> int:
        return len(self._rows)
