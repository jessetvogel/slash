Hello world
===========

The following is a minimal example of using Slash to setup a web page.

.. code-block:: python

    from slash import App
    from slash.html import H1

    def home() -> H1:
        return H1("Hello world!").style({"text-align": "center"})

    def main():
        app = App()
        app.add_route("/", home)
        app.run()

    if __name__ == "__main__":
        main()
