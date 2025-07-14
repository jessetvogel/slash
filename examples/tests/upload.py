from __future__ import annotations

from slash.basic.upload import Upload
from slash.core import Elem, Session
from slash.events import UploadEvent
from slash.html import H2, Div


def onupload(event: UploadEvent):
    summary = "\n".join([f"{file.name} ({file.size} bytes)" for file in event.files])

    session = Session.require()
    session.log(
        "info",
        (f"{len(event.files)} files were uploaded<pre><code>{summary}</code></pre>"),
    )


def test_upload() -> Elem:
    return Div(H2("Upload"), Upload(multiple=True).onupload(onupload))
