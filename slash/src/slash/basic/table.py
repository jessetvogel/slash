from typing import Any

from slash.core import Elem


class Table(Elem):
    def __init__(self, *, max_rows: int | None = 10, has_headers: bool = True) -> None:
        self._table = Elem("table")
        super().__init__("div", self._table, **{"class": "table"})  # type: ignore[arg-type]
        self._max_rows = max_rows
        self._has_headers = has_headers

    @property
    def max_rows(self) -> int | None:
        return self._max_rows

    @max_rows.setter
    def max_rows(self, value: int | None) -> None:
        self._max_rows = value
        # TODO: update layout ?

    @property
    def has_headers(self) -> bool:
        return self._has_headers

    @has_headers.setter
    def has_headers(self, value: bool) -> None:
        self._has_headers = value
        # TODO: Update table? (Can just replace td with th or vice versa)

    def data(self, data: list[list[Any]]) -> None:
        self._table.clear()
        for i, row in enumerate(data):
            cell = "th" if self.has_headers and i == 0 else "td"
            self._table.append(Elem("tr", *[Elem(cell, str(entry)) for entry in row]))
