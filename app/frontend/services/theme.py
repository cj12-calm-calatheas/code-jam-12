from typing import Literal, cast, override

import reactivex.operators as op
from js import document, localStorage
from reactivex.subject import BehaviorSubject

from frontend.base import Service

type Theme_ = Literal["light", "dark"] | None

ATTRIBUTE_NAME = "data-theme"


def _update_document_theme(theme: Theme_) -> None:
    """Set the theme of the document."""
    if theme:
        document.documentElement.setAttribute(ATTRIBUTE_NAME, theme)  # type: ignore[setAttribute not defined]
    else:
        document.documentElement.removeAttribute(ATTRIBUTE_NAME)  # type: ignore[removeAttribute not defined]


LOCAL_STORAGE_KEY = "theme"


def _update_local_storage(theme: Theme_) -> None:
    """Set the theme in local storage."""
    if theme:
        localStorage.setItem(LOCAL_STORAGE_KEY, theme)
    else:
        localStorage.removeItem(LOCAL_STORAGE_KEY)


class Theme(Service):
    """Service to manage the theme of the application."""

    def __init__(self) -> None:
        super().__init__()

        self.current = BehaviorSubject[Theme_](
            cast("Theme_", theme)
            if (theme := localStorage.getItem(LOCAL_STORAGE_KEY)) and theme in {"light", "dark"}
            else None,
        )

        # Update the document theme whenever the current theme changes
        self.current.pipe(
            op.take_until(self.destroyed),
        ).subscribe(_update_document_theme)

        # Update the local storage whenever the current theme changes
        self.current.pipe(
            op.take_until(self.destroyed),
        ).subscribe(_update_local_storage)

    @override
    def on_destroy(self) -> None:
        """Clean up the theme service."""
        self.current.dispose()


theme = Theme()
