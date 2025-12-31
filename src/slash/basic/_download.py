from pathlib import Path

from slash.basic._icon import Icon
from slash.core import Elem, Session
from slash.html import Button


class Download(Elem):
    """Download button element.

    Args:
        path: Path to file to download.
        text: Text shown on the button.
    """

    def __init__(self, path: Path, *, text: str = "Download") -> None:
        super().__init__("a")
        self._path = path

        self.append(Button(Icon("download"), text).style({"display": "inline-flex", "gap": "4px"}))
        self.set_attr("download", path.name)
        self.add_class("slash-download")
        self.onmount(self._setup_download)

    def _setup_download(self) -> None:
        url = Session.require().share_file(self._path)
        self.set_attr("href", url)
