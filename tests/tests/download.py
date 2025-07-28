from __future__ import annotations

from slash._server import PATH_PUBLIC
from slash.basic._download import Download
from slash.core import Elem
from slash.html import Code, Div, P


def test_download() -> Elem:
    file = PATH_PUBLIC / "img" / "favicon.png"
    return Div(
        P("This page tests the ", Code("Download"), " element. Click on the button below to download a file."),
        Download(file, text="Download favicon"),
    )
