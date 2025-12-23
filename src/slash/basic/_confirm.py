from slash.core import Elem, Session
from slash.html import Button, Dialog, Div
from slash.js import JSFunction
from slash.layout import Column, Row

_JS_DELETE_ON_CLOSE = JSFunction(
    ["id"],
    """
const elem = document.getElementById(id);
elem.addEventListener('close', () => elem.remove());
""",
)


async def confirm(message: str | Elem) -> bool:
    """Display confirmation dialog.

    Args:
        message: Message to display in the confirmation dialog.

    Returns:
        Boolean indicating whether OK (`True`) or Cancel (`False`) was selected.
    """
    session = Session.require()
    future = session.create_future()

    def set_result(result: bool) -> None:
        future.set_result(result)
        dialog.unmount()

    dialog = (
        Dialog(
            Column(
                Div(message),
                Row(
                    Button("OK").onclick(lambda: set_result(True)),
                    Button("Cancel").onclick(lambda: set_result(False)),
                ).style({"gap": "8px", "justify-content": "center"}),
            ).style({"gap": "16px"}),
        )
        .mount()
        .show_modal()
    )
    session.execute(_JS_DELETE_ON_CLOSE, [dialog.id])
    await session.flush()

    return await future
