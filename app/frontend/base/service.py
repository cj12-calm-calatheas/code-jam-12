from reactivex import Subject


class Service:
    """Base class for all services."""

    def __init__(self) -> None:
        self.destroyed = Subject[None]()

    def destroy(self) -> None:
        """Destroy the service."""
        self.destroyed.on_next(None)
        self.destroyed.dispose()
        self.on_destroy()

    def on_destroy(self) -> None:
        """Hook to perform actions after the service is destroyed."""
        return
