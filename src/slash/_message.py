from __future__ import annotations

import json
from typing import Any


class Message:
    def __init__(self, event: str, **data: Any) -> None:
        self.event = event
        self.data = data

    def to_json(self) -> str:
        return json.dumps({"event": self.event, **self.data})

    @staticmethod
    def from_json(data: str) -> Message:
        object: dict[str, Any] = json.loads(data)
        event: str = object.pop("event")
        return Message(event, **object)

    @staticmethod
    def create(tag: str, id: str, parent: str, **attrs) -> Message:
        if not attrs.get("onclick", True):
            attrs.pop("onclick")
        if not attrs.get("onupdate", True):
            attrs.pop("onupdate")
        if not attrs.get("style", True):
            attrs.pop("style")
        return Message(event="create", tag=tag, id=id, parent=parent, **attrs)

    @staticmethod
    def remove(id: str) -> Message:
        return Message(event="remove", id=id)

    @staticmethod
    def update(id: str, **attrs) -> Message:
        return Message(event="update", id=id, **attrs)

    @staticmethod
    def clear(id: str) -> Message:
        return Message(event="clear", id=id)

    @staticmethod
    def html(id: str, html: str) -> Message:
        return Message(event="html", id=id, html=html)

    @staticmethod
    def script(script: str) -> Message:
        # NOTE: not recommended
        return Message(event="script", script=script)

    @staticmethod
    def function(name: str, args: list[str], body: str) -> Message:
        return Message(event="function", name=name, args=args, body=body)

    @staticmethod
    def execute(name: str, args: list[Any], store: str | None = None) -> Message:
        if store:
            return Message(event="execute", name=name, args=args, store=store)
        else:
            return Message(event="execute", name=name, args=args)

    @staticmethod
    def log(type: str, title: str, message: str, *, id: str | None = None) -> Message:
        if id is not None:
            return Message(event="log", type=type, title=title, message=message, id=id)
        else:
            return Message(event="log", type=type, title=title, message=message)

    def __repr__(self) -> str:
        return str(self.__dict__)
