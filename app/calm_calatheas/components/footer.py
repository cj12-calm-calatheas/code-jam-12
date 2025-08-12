from typing import override

from js import Event, document
from pyodide.ffi import JsDomElement
from pyodide.ffi.wrappers import add_event_listener

from calm_calatheas.base import Component
from calm_calatheas.services import camera

from .camera import Camera

TEMPLATE = """
<nav class="tabs is-boxed is-fullwidth">
    <ul>
        <li>
            <button id="camera-button" class="button is-large is-fullwidth is-text">
                <span class="icon is-large has-text-primary">
                    <i class="fa-regular fa-camera"></i>
                </span>
            </button>
        </li>
    </ul>
</nav>
"""


class Footer(Component):
    """Footer for the application."""

    def __init__(self, root: JsDomElement) -> None:
        super().__init__(root)
        self._camera = camera

    @override
    def build(self) -> str:
        return TEMPLATE

    @override
    def pre_destroy(self) -> None:
        if hasattr(self, "_overlay"):
            self._overlay.destroy()

    @override
    def on_render(self) -> None:
        self._camera_button = document.getElementById("camera-button")
        add_event_listener(self._camera_button, "click", self._on_camera_button_click)

    def _on_camera_button_click(self, _: Event) -> None:
        self._overlay = Camera(self.root)
        self._overlay.render()
