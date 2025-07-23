from __future__ import annotations

from slash.basic.upload import Upload
from slash.core import Elem, Session
from slash.events import UploadEvent
from slash.html import Div, Img


def onupload(event: UploadEvent, img: Img):
    summary = "\n".join([f"{file.name} ({file.size} bytes)" for file in event.files])

    session = Session.require()
    session.log("info", (f"{len(event.files)} files were uploaded<pre><code>{summary}</code></pre>"), format="html")

    for file in event.files:
        if file.path.suffix in [".png", ".jpg", ".jpeg"]:
            img.src = session.host(file.path)
            break


def test_upload() -> Elem:
    return Div(
        Upload(text="Drop an image here!", multiple=False).onupload(lambda event: onupload(event, img)),
        img := Img("").style({"max-width": "100%"}),
    )
