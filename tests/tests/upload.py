from __future__ import annotations

from slash.basic._upload import Upload
from slash.core import Elem, Session
from slash.events import UploadEvent
from slash.html import Code, Div, Img, P, Pre


def onupload(event: UploadEvent, img: Img):
    summary = "\n".join([f"{file.name} ({file.size} bytes)" for file in event.files])

    session = Session.require()
    session.log(f"{len(event.files)} files were uploaded", level="info", details=Pre(Code(summary)))

    for file in event.files:
        if file.path.suffix in [".png", ".jpg", ".jpeg"]:
            img.src = session.share_file(file.path)
            break


def test_upload() -> Elem:
    return Div(
        P(
            "This page tests the ",
            Code("Upload"),
            " element. ",
            "Upload an image using the field below, and it should appear below it.",
        ),
        Upload(text="Drop an image here!", multiple=False).onupload(lambda event: onupload(event, img)),
        img := Img().style({"max-width": "100%"}),
    )
