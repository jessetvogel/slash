from slash.core import Attr, Elem


class Image(Elem):
    src = Attr("src")
    alt = Attr("alt")

    def __init__(self, src: str, *, alt: str = "") -> None:
        super().__init__("img")
        self.src = src
        self.alt = alt
