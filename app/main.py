from frontend import App
from js import document


def bootstrap() -> None:
    """Bootstrap the application to the DOM."""
    app = App(document.body)
    app.render()


if __name__ == "__main__":
    bootstrap()
