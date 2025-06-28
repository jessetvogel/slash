from typing import Self

import markdown as md

from slash.html import HTML


class Markdown(HTML):
    def __init__(self, markdown: str) -> None:
        super().__init__("")
        self.set_markdown(markdown)

    def set_markdown(self, markdown) -> Self:
        self.set_html(md.markdown(markdown))
        return self
