from typing import TYPE_CHECKING, Optional, cast, override

import reactivex.operators as op
from js import Blob, Event, MediaStream, document
from pyodide.ffi import JsDomElement, create_once_callable
from pyodide.ffi.wrappers import add_event_listener

from frontend.base import Component
from frontend.services import Camera as CameraService
from frontend.services import reader

if TYPE_CHECKING:
    from js import JsVideoElement


TEMPLATE = """
<div class="modal is-active">
    <div class="modal-background"></div>
    <div class="modal-content">
        <figure id="camera-container" class="image is-4by3">
            <video id="camera-stream" width="100%" autoplay playsinline></video>
        </figure>
        <div class="buttons has-addons is-centered is-large mt-5">
            <button id="camera-capture" class="button is-success is-large is-expanded">Capture</button>
            <button id="camera-switch" class="button is-large">
                <span class="icon">
                    <i class="fa-solid fa-repeat"></i>
                </span>
            </button>
        </div>
    </div>
    <button id="camera-close" class="modal-close is-large" aria-label="close"></button>
</div>
"""


class Camera(Component):
    """Component for displaying the camera feed."""

    def __init__(self, root: JsDomElement) -> None:
        super().__init__(root)
        self._camera = CameraService()

    @override
    def build(self) -> str:
        return TEMPLATE

    @override
    def on_destroy(self) -> None:
        self._camera.destroy()

    @override
    def on_render(self) -> None:
        self._camera_capture = document.getElementById("camera-capture")
        self._camera_container = document.getElementById("camera-container")
        self._camera_close = document.getElementById("camera-close")
        self._camera_stream = cast("JsVideoElement", document.getElementById("camera-stream"))
        self._camera_switch = document.getElementById("camera-switch")

        add_event_listener(self._camera_capture, "click", self._handle_capture)
        add_event_listener(self._camera_close, "click", self._handle_close)
        add_event_listener(self._camera_switch, "click", self._handle_toggle_facing_mode)

        # Update the UI whenever the media stream is being acquired
        self._camera.is_acquiring_media_stream.pipe(
            op.take_until(self.destroyed),
        ).subscribe(lambda status: self._handle_is_acquiring_media_stream(status=status))

        # Update the UI whenever the media stream is available
        self._camera.media_stream.pipe(
            op.take_until(self.destroyed),
        ).subscribe(self._handle_media_stream)

        self._camera.acquire_media_stream()

    def _handle_capture(self, event: Event) -> None:
        """Capture a snapshot from the camera stream."""
        if event.currentTarget.hasAttribute("disabled"):  # type: ignore[currentTarget is available]
            return

        canvas = document.createElement("canvas")
        canvas.width = self._camera_stream.videoWidth
        canvas.height = self._camera_stream.videoHeight

        context = canvas.getContext("2d")

        context.drawImage(
            self._camera_stream,
            0,
            0,
            self._camera_stream.videoWidth,
            self._camera_stream.videoHeight,
        )

        canvas.toBlob(create_once_callable(self._handle_capture_success), "image/png")

    def _handle_capture_success(self, blob: Blob) -> None:
        """Send the captured image to the reader."""
        reader.read(blob)
        self.destroy()

    def _handle_close(self, _: Event) -> None:
        """Close the camera modal."""
        self.destroy()

    def _handle_is_acquiring_media_stream(self, *, status: bool) -> None:
        """Set the spinner on the capture button."""
        if status:
            self._camera_capture.classList.add("is-loading")
        else:
            self._camera_capture.classList.remove("is-loading")

    def _handle_media_stream(self, stream: Optional[MediaStream]) -> None:
        """
        Set the camera stream source.

        If no source is given, disable the controls and show a loading indicator.
        """
        self._camera_stream.srcObject = stream

        if not stream:
            self._camera_capture.setAttribute("disabled", "")
            self._camera_switch.setAttribute("disabled", "")
            self._camera_container.classList.add("is-skeleton")
        else:
            self._camera_capture.removeAttribute("disabled")
            self._camera_switch.removeAttribute("disabled")
            self._camera_container.classList.remove("is-skeleton")

    def _handle_toggle_facing_mode(self, event: Event) -> None:
        """Switch the preferred facing mode between user and environment."""
        if event.currentTarget.hasAttribute("disabled"):  # type: ignore[currentTarget is available]
            return

        self._camera.toggle_facing_mode()
