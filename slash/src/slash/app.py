import json
import random
from slash.elem import Elem
from slash.server import Server


class App:
    def __init__(self):
        self.pages = {}

    def add_page(self, endpoint: str, page: Elem):
        self.pages[endpoint] = page

    def run(self):
        print("test")
        server = Server("127.0.0.1", 8080)

        server.on_ws_connect(on_ws_connect)
        server.on_ws_message(on_ws_message)

        server.serve()


def on_ws_connect() -> list[str]:
    return [
        json.dumps(
            {
                "event": "create",
                "id": "abcdef",
                "parent": "body",
                "tag": "div",
                "style": {
                    "background-color": "red",
                    "width": "100px",
                    "height": "100px",
                },
                "onclick": True,
            }
        ),
        json.dumps(
            {
                "event": "create",
                "id": "12345",
                "parent": "abcdef",
                "tag": "span",
            }
        ),
    ]


def on_ws_message(message: str) -> list[str]:
    msg = json.loads(message)

    if msg["event"] == "click":
        return [
            json.dumps(
                {
                    "event": "update",
                    "id": "abcdef",
                    "style": {"background-color": random_hex_color()},
                }
            )
        ]

    return []


def random_hex_color() -> str:
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))
