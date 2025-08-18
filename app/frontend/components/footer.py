from typing import TYPE_CHECKING, cast, override

import reactivex.operators as op
from js import Event, document
from pyodide.ffi.wrappers import add_event_listener
from reactivex import combine_latest

from frontend.base import Component
from frontend.services import caption, pokemon, reader

from .camera import Camera

if TYPE_CHECKING:
    from js import JsButtonElement, JsFileInputElement

TEMPLATE = """
<nav class="tabs is-boxed is-fullwidth">
    <ul>
        <li>
            <a id="camera-button" class="is-size-4">
                <span class="icon is-large has-text-primary">
                    <i class="fa-regular fa-camera"></i>
                </span>
            </a>
        </li>
        <li>
            <input
                id="file-input"
                class="file-input"
                type="file" name="file"
                accept="image/png, image/jpeg"
                style="display: none;"
            />
            <a id="upload-button" class="is-size-4">
                <span class="icon is-large has-text-primary">
                    <i class="fas fa-upload"></i>
                </span>
            </a>
        </li>
    </ul>
</nav>
"""


class Footer(Component):
    """Footer for the application."""

    @override
    def build(self) -> str:
        return TEMPLATE

    @override
    def pre_destroy(self) -> None:
        if hasattr(self, "_overlay"):
            self._overlay.destroy()

    @override
    def on_render(self) -> None:
        self._camera_button = cast(
            "JsButtonElement",
            document.getElementById("camera-button"),
        )
        self._file_input = cast(
            "JsFileInputElement",
            document.getElementById("file-input"),
        )
        self._upload_button = cast(
            "JsButtonElement",
            document.getElementById("upload-button"),
        )

        # Disable the controls while the model is loading or generating
        combine_latest(caption.is_loading_model, pokemon.is_generating).pipe(
            op.map(lambda is_loading: any(is_loading)),
        ).subscribe(
            lambda is_loading: self._handle_is_loading(
                is_loading=is_loading,
            ),
        )

        add_event_listener(self._camera_button, "click", self._on_camera_button_click)
        add_event_listener(self._file_input, "change", self._on_file_input_change)
        add_event_listener(self._upload_button, "click", self._on_upload_button_click)

    def _handle_is_loading(self, *, is_loading: bool) -> None:
        """Handle the loading state of the footer."""
        if is_loading:
            self._camera_button.setAttribute("disabled", "")
            self._file_input.setAttribute("disabled", "")
            self._upload_button.setAttribute("disabled", "")
        else:
            self._camera_button.removeAttribute("disabled")
            self._file_input.removeAttribute("disabled")
            self._upload_button.removeAttribute("disabled")

    def _on_camera_button_click(self, event: Event) -> None:
        if event.currentTarget.hasAttribute("disabled"):  # type: ignore[currentTarget is available]
            return

        self._overlay = Camera(self.root)
        self._overlay.render()

    def _on_file_input_change(self, event: Event) -> None:
        if event.target.hasAttribute("disabled"):
            return

        files = self._file_input.files
        if files.length:
            reader.read(files.item(0))

    def _on_upload_button_click(self, event: Event) -> None:
        if event.currentTarget.hasAttribute("disabled"):  # type: ignore[currentTarget is available]
            return

        self._file_input.click()
