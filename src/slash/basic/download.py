from pathlib import Path

from slash.core import Elem, Session


class Download(Elem):
    def __init__(self, file: Path, *, text: str = "Download") -> None:
        super().__init__("a", text)
        self.set_attr("download", file.name)
        self.add_class("slash-download")

        self._file = file

        self.onmount(self._setup_download)

    def _setup_download(self) -> None:
        session = Session.require()

        url = session.host(self._file)
        self.set_attr("href", url)
