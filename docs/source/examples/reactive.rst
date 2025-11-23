Reactive page
=============

The classes :py:class:`~slash.reactive.Signal`, :py:class:`~slash.reactive.Computed` and :py:class:`~slash.reactive.Effect` from the :py:mod:`slash.reactive` module can be used to build a reactive web page.

- A :py:class:`~slash.reactive.Signal` holds a value.
- A :py:class:`~slash.reactive.Computed` holds a value that is computed from the values of other :py:class:`~slash.reactive.Signal` or :py:class:`~slash.reactive.Computed` instances.
- An :py:class:`~slash.reactive.Effect` executes a function every time the value of a :py:class:`~slash.reactive.Signal` or :py:class:`~slash.reactive.Computed` changes that it depends on.


.. code-block:: python

    from datetime import datetime
    from slash import App
    from slash.core import Session
    from slash.reactive import Signal, Computed, Effect
    from slash.html import Input

    def home():
        # Create two signals with initial values
        name = Signal("Mickey")
        year = Signal(2024)

        # Compute values from other values
        age = Computed(lambda: datetime.now().year - year())
        text = Computed(lambda: f"{name()} is {age()} years old")

        # This effect executes every time the value of `text` changes
        Effect(lambda: Session.require().log(text()))

        # The `.to_elem` method creates an element whose content is
        # set to the value of the Signal or Computed.
        return Div(
            Input(value=name()).onchange(lambda event: name.set(event.value)),
            Input("number", value=str(year())).onchange(lambda event: year.set(int(event.value))),
            text.to_elem("span")
        )

    if __name__ == "__main__":
        app = App()
        app.add_route("/", home)
        app.run()
