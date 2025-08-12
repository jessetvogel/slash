Handling events
===============

When the user interacts with the elements on the page, these events are sent to the server where they can be handled.
Examples of such events are :py:class:`~slash.events.ClickEvent`, :py:class:`~slash.events.ChangeEvent`, :py:class:`~slash.events.InputEvent`, etc.
The following example shows how event handlers can be attached to elements.

.. code-block:: python

    from slash import App
    from slash.core import Session
    from slash.html import A, Button, Div
    from slash.events import ClickEvent

    def click_handler(event: ClickEvent) -> None:
        Session.require().log("info", f"You clicked the <{event.target.tag}> element!")

    def home() -> Div:
        return Div(
            A("Click me!").onclick(click_handler),
            Button("Or click me!").onclick(click_handler),
        )

    def main():
        app = App()
        app.add_route("/", home)
        app.run()

    if __name__ == "__main__":
        main()


The :py:class:`~slash.events.MountEvent` and :py:class:`~slash.events.UnmountEvent` events are fired when an element is mounted and unmounted on the page, respectively.
The following example shows how handlers for these events can be attached to elements.

.. code-block:: python

    import random
    from slash import App
    from slash.core import Session, MountEvent, UnmountEvent
    from slash.html import Button, Div
    from slash.layout import Row

    def mount_handler(event: MountEvent) -> None:
        Session.require().log("info", f"The {event.target.text} circle was mounted!")

    def unmount_handler(event: UnmountEvent) -> None:
        Session.require().log("info", f"The {event.target.text} circle was unmounted!")

    def circle() -> Div:
        color = random.choice(["red", "yellow", "blue", "green"])
        return (
            Div(color)
            .style(
                {
                    "background-color": f"var(--{color})",
                    "width": "48px",
                    "height": "48px",
                    "border-radius": "100%",
                    "line-height": "48px",
                    "text-align": "center",
                    "cursor": "pointer"
                }
            )
            .onmount(mount_handler)
            .onunmount(unmount_handler)
            .onclick(lambda event: event.target.unmount())
        )

    def home() -> Div:
        return Div(
            Button("Add circle").onclick(lambda: row.append(circle())),
            row := Row().style({"gap": "8px"})
        )

    def main():
        app = App()
        app.add_route("/", home)
        app.run()

    if __name__ == "__main__":
        main()
