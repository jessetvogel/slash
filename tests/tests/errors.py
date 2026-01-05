from __future__ import annotations

from slash.core import Elem
from slash.html import Button, P
from slash.layout import Column


def raise_error() -> None:
    raise RuntimeError("Hi, I'm an error!")


async def raise_error_async() -> None:
    raise RuntimeError("Hi, I'm an async error!")


def invalid_callback(x: int, y: int) -> None:
    pass


def test_errors() -> Elem:
    return Column(
        P("This page tests that exceptions in callbacks are catched correctly."),
        Button("Raise error in callback").onclick(raise_error),
        Button("Raise error in async callback").onclick(raise_error_async),
        Button("Raise error due to invalid callback").onclick(invalid_callback),  # ty: ignore[invalid-argument-type]
    ).style({"gap": "16px"})
