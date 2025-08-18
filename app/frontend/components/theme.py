from typing import TYPE_CHECKING, cast, override

import reactivex.operators as op
from js import Event, document
from pyodide.ffi.wrappers import add_event_listener

from frontend.base import Component
from frontend.services import Theme_, theme

if TYPE_CHECKING:
    from js import JsAnchorElement

TEMPLATE = """
<div class="navbar-item has-dropdown is-hoverable">
    <span class="navbar-link is-arrowless">
        Theme
    </span>
    <div class="navbar-dropdown">
        <a id="select-theme-light" class="navbar-item">
            Light
        </a>
        <a id="select-theme-dark" class="navbar-item">
            Dark
        </a>
        <a id="select-theme-auto" class="navbar-item">
            Auto
        </a>
    </div>
</div>
"""


class Theme(Component):
    """A component for selecting the theme."""

    @override
    def build(self) -> str:
        return TEMPLATE

    @override
    def on_destroy(self) -> None:
        self._current_theme_listener.dispose()

    @override
    def on_render(self) -> None:
        self._select_theme_light = cast("JsAnchorElement", document.getElementById("select-theme-light"))
        self._select_theme_dark = cast("JsAnchorElement", document.getElementById("select-theme-dark"))
        self._select_theme_auto = cast("JsAnchorElement", document.getElementById("select-theme-auto"))

        add_event_listener(self._select_theme_light, "click", self._set_theme_light)
        add_event_listener(self._select_theme_dark, "click", self._set_theme_dark)
        add_event_listener(self._select_theme_auto, "click", self._set_theme_auto)

        # Update the UI whenever the current theme changes
        self._current_theme_listener = theme.current.pipe(
            op.take_until(self.destroyed),
        ).subscribe(lambda theme: self._update_current_theme(theme))

    def _set_theme_light(self, _: Event) -> None:
        """Set the theme to light."""
        theme.current.on_next("light")

    def _set_theme_dark(self, _: Event) -> None:
        """Set the theme to dark."""
        theme.current.on_next("dark")

    def _set_theme_auto(self, _: Event) -> None:
        """Set the theme to auto."""
        theme.current.on_next(None)

    def _update_current_theme(self, theme: Theme_) -> None:
        """Set the active state on the appropriate theme selector."""
        if theme == "light":
            self._select_theme_light.classList.add("is-active")
            self._select_theme_dark.classList.remove("is-active")
            self._select_theme_auto.classList.remove("is-active")
        elif theme == "dark":
            self._select_theme_dark.classList.add("is-active")
            self._select_theme_light.classList.remove("is-active")
            self._select_theme_auto.classList.remove("is-active")
        else:
            self._select_theme_auto.classList.add("is-active")
            self._select_theme_light.classList.remove("is-active")
            self._select_theme_dark.classList.remove("is-active")
