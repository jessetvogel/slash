import functools
from numbers import Real
from typing import Any, Literal, Mapping, Self, Sequence, TypeAlias

from slash.core import Elem
from slash.html import Button, Div, Label, Span, Td, Th, Tr

Datum: TypeAlias = Mapping[str, int | float | str | Elem]


class DataTable(Elem):
    """Table for displaying rows of data.

    Args:
        keys: Sequence of column headings.
        max_rows: Maximum number of rows displayed at once.
    """

    def __init__(self, keys: Sequence[str], *, max_rows: int = 10) -> None:
        super().__init__("div")
        self.add_class("slash-data-table")
        self._keys = list(keys)
        self._max_rows = max_rows

        self._table = Elem("table").style({"width": "100%"})
        self._controls = Div(
            first := Button().add_class("first").onclick(lambda: self._goto_page("first")),
            prev := Button().add_class("prev").onclick(lambda: self._goto_page("prev")),
            span := Span(),
            next := Button().add_class("next").onclick(lambda: self._goto_page("next")),
            last := Button().add_class("last").onclick(lambda: self._goto_page("last")),
        ).add_class("controls")
        self.append(self._table)
        self.append(self._controls)

        self._controls_first = first
        self._controls_prev = prev
        self._controls_span = span
        self._controls_next = next
        self._controls_last = last

        self._data: Sequence[Datum] = []
        self._index = 0
        self._sort_key: str | None

        self._init_table()

    @property
    def max_rows(self) -> int:
        return self._max_rows

    @max_rows.setter
    def max_rows(self, max_rows: int) -> None:
        self._max_rows = max_rows
        self._init_table()

    def set_max_rows(self, max_rows: int) -> Self:
        self.max_rows = max_rows
        return self

    def _goto_page(self, action: Literal["first", "prev", "next", "last"]) -> None:
        if action == "first":
            if self._index > 0:
                self._index = 0
                self._update_data()
        elif action == "prev":
            if self._index > 0:
                self._index = max(0, self._index - self._max_rows)
                self._update_data()
        elif action == "next":
            if self._index + self._max_rows < len(self._data):
                self._index += self._max_rows
                self._update_data()
        elif action == "last":
            last_index = (len(self._data) - 1) // self._max_rows * self._max_rows
            if self._index < last_index:
                self._index = last_index
                self._update_data()

    def _set_sort_key(self, key: str | None) -> None:
        if not hasattr(self, "_sort_key") or self._sort_key is None or self._sort_key != key:
            self._sort_key = key
            self._sort_asc = True
            self._update_sort_indices()
        else:
            if self._sort_asc:
                self._sort_asc = False
            else:
                self._sort_key = None
                self._update_sort_indices()

        self._update_sort()
        self._update_data()

    def _update_sort_indices(self) -> None:
        if self._sort_key is None:
            self._sort_indices = None
        else:
            sort_key = self._sort_key

            def compare(i: int, j: int) -> Any:
                value_i = self._data[i].get(sort_key)
                value_j = self._data[j].get(sort_key)

                if isinstance(value_i, Elem):  # compare `Elem` based on text
                    value_i = value_i.text
                if isinstance(value_j, Elem):  # compare `Elem` based on text
                    value_j = value_j.text

                if value_i == value_j:  # same values
                    return 0
                if value_i is None:  # `None` is always last
                    return 1
                if value_j is None:  # `None` is always last
                    return -1
                NUMERIC = (int, float, Real)
                if isinstance(value_i, NUMERIC) and isinstance(value_j, NUMERIC):  # compare numbers
                    return value_i - value_j
                if isinstance(value_i, NUMERIC):  # numbers before strings
                    return -1
                if isinstance(value_j, NUMERIC):  # numbers before strings
                    return 1

                return int(value_i > value_j) - int(value_i < value_j)

            self._sort_indices = sorted(range(len(self._data)), key=functools.cmp_to_key(compare))

    def _update_sort(self) -> None:
        """Update sort labels in table header."""
        for key, th in zip(self._keys, self._table_header.children):
            assert isinstance(th, Th)
            label = th.children[0]
            assert isinstance(label, Label)
            label.remove_class("asc desc")
            if key == self._sort_key:
                label.add_class("asc" if self._sort_asc else "desc")

    def _update_controls(self) -> None:
        """Update controls"""
        # Update buttons
        is_first = self._index == 0
        is_last = self._index >= (len(self._data) - 1) // self.max_rows * self.max_rows
        for control, disabled in [
            (self._controls_first, is_first),
            (self._controls_prev, is_first),
            (self._controls_next, is_last),
            (self._controls_last, is_last),
        ]:
            if disabled:
                control.add_class("disabled")
            else:
                control.remove_class("disabled")

        # Update span
        start = 1 + self._index
        end = min(self._index + self.max_rows, len(self._data))
        self._controls_span.set_text(f"{start}–{end} / {len(self._data)}")

    def _update_data(self) -> None:
        """Update table data."""
        for i, tr in zip(range(self._max_rows), self._table.children[1:]):
            assert isinstance(tr, Tr)
            index = self._index + i
            if index >= len(self._data):
                tr.style({"display": "none"})
                continue
            tr.style({"display": None})
            if self._sort_indices is not None:
                index = self._sort_indices[index] if self._sort_asc else self._sort_indices[len(self._data) - 1 - index]
            datum = self._data[index]
            for key, td in zip(self._keys, tr.children):
                assert isinstance(td, Td)
                cell: Elem | str
                if key not in datum or datum[key] is None:
                    cell = Span("-").style({"color": "var(--text-muted)"})
                else:
                    value = datum[key]
                    cell = value if isinstance(value, Elem) else str(value)
                td.clear()
                td.append(cell)

        self._update_controls()

    def _init_table(self) -> None:
        self._table.clear()
        # Table header
        self._table_header = Tr(
            [
                Th(Label().add_class("sort"), key).onclick(lambda event: self._set_sort_key(event.target.children[1]))
                for key in self._keys
            ]
        )
        self._table.append(self._table_header)
        # Table data rows
        for _ in range(self._max_rows):
            self._table.append(Tr([Td() for _ in self._keys]))
        # Update table
        self._set_sort_key(None)
        self._update_sort()
        self._update_data()
        self._update_controls()

    def set_keys(self, keys: Sequence[str]) -> Self:
        """Set keys for table columns.

        Args:
            keys: Sequence of column headings.
        """
        self._keys = list(keys)
        if self._sort_key not in self._keys:
            self._set_sort_key(None)
        self._update_sort_indices()
        self._init_table()
        return self

    def set_data(self, data: Sequence[Datum]) -> Self:
        """Set data for table contents.

        Args:
            data: Sequence of rows of data, each row being a mapping whose keys
                correspond to the `keys` of the table and whose values are the data.
        """
        self._data = data
        self._index = 0
        self._update_sort_indices()
        self._update_data()
        return self
