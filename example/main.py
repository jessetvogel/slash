from slash.app import App
import slash.elem as e


def main():
    home = e.Div(
        [
            e.Span("Hello"),
            e.Span("world!"),
        ]
    )

    app = App()
    app.add_page("/", home)
    app.run()


if __name__ == "__main__":
    main()
