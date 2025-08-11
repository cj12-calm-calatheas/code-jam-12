from typing import override

from js import Event, document
from pyodide.ffi import JsDomElement
from pyodide.ffi.wrappers import add_event_listener

from calm_calatheas.base import Component

from .theme import Theme

TEMPLATE = """
<nav class="navbar" role="navigation" aria-label="main navigation">
    <div class="navbar-brand">
        <span class="navbar-item">
            Calm Calatheas
        </span>
        <span id="navbar-burger" class="navbar-burger has-text-primary" data-target="main-navigation">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
        </span>
    </div>
    <div id="main-navigation" class="navbar-menu">
        <div id="navbar-end" class="navbar-end"></div>
    </div>
</nav>
"""


class Header(Component):
    """The main header for the application."""

    def __init__(self, root: JsDomElement) -> None:
        super().__init__(root)
        self._expanded = False

    @override
    def build(self) -> str:
        return TEMPLATE

    @override
    def pre_destroy(self) -> None:
        self._theme_selector.destroy()

    @override
    def on_render(self) -> None:
        self._theme_selector = Theme(document.getElementById("navbar-end"))
        self._theme_selector.render()

        self._main_navigation = document.getElementById("main-navigation")
        self._navbar_burger = document.getElementById("navbar-burger")

        add_event_listener(self._navbar_burger, "click", self._toggle_navbar)

    @property
    def expanded(self) -> bool:
        """Whether or not the navbar menu is expanded."""
        return self._expanded

    @expanded.setter
    def expanded(self, value: bool) -> None:
        self._expanded = value

        if value:
            self._main_navigation.classList.add("is-active")
            self._navbar_burger.classList.add("is-active")
        else:
            self._main_navigation.classList.remove("is-active")
            self._navbar_burger.classList.remove("is-active")

    def _toggle_navbar(self, _: Event) -> None:
        self.expanded = not self.expanded
