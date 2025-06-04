from slash.core import Elem


class Image(Elem):
    def __init__(self, src: str, *, alt: str = "") -> None:
        super().__init__("img")
        self._src = src
        self._alt = alt

    @property
    def src(self) -> str:
        return self._src

    @src.setter
    def src(self, value: str) -> None:
        self._src = value
        self.update_attrs({"src": value})

    @property
    def alt(self) -> str:
        return self._alt

    @alt.setter
    def alt(self, value: str) -> None:
        self._alt = value
        self.update_attrs({"alt": value})

    def attrs(self) -> dict[str, str]:
        return {"src": self._src, "alt": self._alt}
