import random
import string


def random_id() -> str:
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return "_" + "".join(random.choices(characters, k=8))


class JSFunction:
    def __init__(self, args: list[str], body: str) -> None:
        self._id = random_id()
        self._args = args
        self._body = body

    @property
    def id(self) -> str:
        return self._id

    @property
    def args(self) -> list[str]:
        return self._args

    @property
    def body(self) -> str:
        return self._body
