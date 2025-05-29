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
        return Message(event="create", tag=tag, id=id, parent=parent, **attrs)

    @staticmethod
    def remove(id: str) -> Message:
        return Message(event="remove", id=id)

    @staticmethod
    def update(id: str, **attrs) -> Message:
        return Message(event="update", id=id, **attrs)

    @staticmethod
    def script(script: str) -> Message:
        # NOTE: not recommended
        return Message(event="script", script=script)

    @staticmethod
    def func(name: str, args: list[str], body: str) -> Message:
        return Message(event="func", name=name, args=args, body=body)

    @staticmethod
    def exec(func: str, args: list[str | int | float]) -> Message:
        return Message(event="exec", func=func, args=args)


# class Create(Message):
#     def __init__(self, tag: str, id: str, parent: str, **attrs) -> None:
#         self.tag = tag
#         self.id = id
#         self.parent = parent
#         self.attrs = attrs

#     def to_json(self) -> str:
#         return json.dumps(
#             {
#                 "event": self.event,
#                 "tag": self.tag,
#                 "id": self.id,
#                 "parent": self.parent,
#                 **self.attrs,
#             }
#         )
