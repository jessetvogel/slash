from __future__ import annotations

from slash._server import PATH_PUBLIC
from slash.basic.download import Download
from slash.core import Elem
from slash.html import H2, Div


def test_download() -> Elem:
    file = PATH_PUBLIC / "img" / "favicon.png"
    return Div(H2("Download"), Download(file, text="Download favicon"))
