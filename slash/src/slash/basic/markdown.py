import markdown as md

from slash.html import HTML


class Markdown(HTML):
    def __init__(self, markdown: str) -> None:
        super().__init__(md.markdown(markdown))
