import json
from pathlib import Path

from slash.core import Elem, Session
from slash.html import H2, Button, Input, Span
from slash.layout import Column, Row


def storage_path() -> Path:
    return Path("./tmp/__slash_storage__") / (Session.require().id + ".txt")


def set_data(key: str, value: str) -> None:
    path = storage_path()
    path.parent.mkdir(exist_ok=True, parents=True)
    if not path.exists():
        data = {}
    else:
        with path.open("r") as file:
            try:
                data = json.load(file)
            except Exception:
                data = {}
    data[key] = value
    with path.open("w") as file:
        json.dump(data, file)


def get_data(key: str) -> str | None:
    path = storage_path()
    path.parent.mkdir(exist_ok=True, parents=True)
    if not path.exists():
        return None
    with path.open("r") as file:
        try:
            data = json.load(file)
        except Exception:
            data = {}
    if not isinstance(data, dict):
        return None
    if key not in data:
        return None
    value = data.get(key)
    if not isinstance(value, str):
        return None
    return value


def update_span(span: Span) -> None:
    value = get_data("test_storage") or "<none>"
    span.set_text("Current value: " + value).style({"padding": "8px"})


def update_storage(value: str, span: Span) -> None:
    set_data("test_storage", value)
    update_span(span)


def test_storage() -> Elem:
    return Column(
        H2("Storage"),
        span := Span().onmount(lambda: update_span(span)),
        Row(
            input := Input(placeholder="Enter new value here"),
            Button("Store").onclick(lambda: update_storage(input.value, span)),
        ),
    )
