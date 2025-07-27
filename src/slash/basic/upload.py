from typing import Self

from slash._server import UploadEvent
from slash.core import Elem, Handler, Session
from slash.html import Input, Label
from slash.js import JSFunction


class Upload(Elem):
    JS_SETUP_FORM = JSFunction(
        ["form_id", "label_id", "input_id"],
        (
            "const form = document.getElementById(form_id);"
            "const label = document.getElementById(label_id);"
            "const input = document.getElementById(input_id);"
            ""
            "async function upload() {"
            "    try {"
            "        const response = await fetch(form.action, {"
            "            method: 'POST',"
            "            body: new FormData(form)"
            "        });"
            "        const text = await response.text();"
            "        if (!response.ok)"
            '            Slash.message("error", text);'
            "    } catch (err) {"
            '        Slash.message("error", `Failed to upload files: ${err.message}`);'
            "    }"
            "}"
            ""
            "label.ondragover = (e) => e.preventDefault();"
            "label.ondragenter = (e) => {"
            "    e.preventDefault();"
            '    label.classList.add("drag");'
            "};"
            "label.ondragleave = (e) => {"
            "    e.preventDefault();"
            '    label.classList.remove("drag");'
            "};"
            "label.ondrop = async (e) => {"
            "    e.preventDefault();"
            '    label.classList.remove("drag");'
            "    const dt = new DataTransfer();"
            "    for (const file of e.dataTransfer.files)"
            "        dt.items.add(file);"
            "    input.files = dt.files;"
            "    if (dt.files.length > 0)"
            "        await upload();"
            "};"
            'input.addEventListener("change", upload);'
        ),
    )

    def __init__(self, *, text: str = "Drop files or click to upload", multiple: bool = False) -> None:
        super().__init__("form", method="POST")
        self.add_class("slash-upload")
        self.onmount(self._setup_form)
        self.append(label := Label(text, input := Input("file", name="file").set_attr("required", "")))
        if multiple:
            input.set_attr("multiple", "")

        self._label_id = label.id
        self._input_id = input.id
        self._onupload_handlers: list[Handler[UploadEvent]] = []

    def onupload(self, handler: Handler[UploadEvent]) -> Self:
        self._onupload_handlers.append(handler)
        return self

    def upload(self, event: UploadEvent) -> None:
        """Trigger upload event."""
        session = Session.require()
        for handler in self._onupload_handlers:
            session.call_handler(handler, event)

    def _setup_form(self) -> None:
        session = Session.require()

        url = session.accept_file(self.upload)
        self.set_attr("action", url)

        session.execute(Upload.JS_SETUP_FORM, [self.id, self._label_id, self._input_id])
