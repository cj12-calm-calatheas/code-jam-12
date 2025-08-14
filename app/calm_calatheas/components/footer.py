from typing import TYPE_CHECKING, cast, override

from js import Event, document
from pyodide.ffi import JsDomElement
from pyodide.ffi.wrappers import add_event_listener

from calm_calatheas.base import Component
from calm_calatheas.services import reader

from .camera import Camera

if TYPE_CHECKING:
    from js import JsButtonElement, JsFileInputElement

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
        <li>
            <input
                id="file-input"
                class="file-input"
                type="file" name="file"
                accept="image/png, image/jpeg"
                style="display: none;"
            />
            <button id="upload-button" class="button is-large is-fullwidth is-text">
                <span class="icon is-large has-text-primary">
                    <i class="fas fa-upload"></i>
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
        self._reader = reader

    @override
    def build(self) -> str:
        return TEMPLATE

    @override
    def pre_destroy(self) -> None:
        if hasattr(self, "_overlay"):
            self._overlay.destroy()

    @override
    def on_render(self) -> None:
        self._camera_button = cast("JsButtonElement", document.getElementById("camera-button"))
        self._file_input = cast("JsFileInputElement", document.getElementById("file-input"))
        self._upload_button = cast("JsButtonElement", document.getElementById("upload-button"))

        add_event_listener(self._camera_button, "click", self._on_camera_button_click)
        add_event_listener(self._file_input, "change", self._on_file_input_change)
        add_event_listener(self._upload_button, "click", self._on_upload_button_click)

    def _on_camera_button_click(self, _: Event) -> None:
        self._overlay = Camera(self.root)
        self._overlay.render()

    def _on_file_input_change(self, _: Event) -> None:
        files = self._file_input.files
        if files.length:
            self._reader.read(files.item(0))

    def _on_upload_button_click(self, _: Event) -> None:
        self._file_input.click()
