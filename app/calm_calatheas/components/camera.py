from typing import TYPE_CHECKING, Optional, cast, override

from js import URL, Blob, MediaStream, document
from pyodide.ffi import JsDomElement, create_once_callable
from pyodide.ffi.wrappers import add_event_listener

from calm_calatheas.base import Component
from calm_calatheas.services import camera

if TYPE_CHECKING:
    from js import JsVideoElement


TEMPLATE = """
<div class="modal is-active">
    <div class="modal-background"></div>
    <div class="modal-content">
        <video id="camera-stream" width="100%" autoplay playsinline></video>
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
        self._camera = camera

    @override
    def build(self) -> str:
        return TEMPLATE

    @override
    def on_destroy(self) -> None:
        self._subscription_is_acquiring_media_stream.dispose()
        self._subscription_media_stream.dispose()
        self._camera.dispose_media_stream()

    @override
    def on_render(self) -> None:
        self._camera_capture = document.getElementById("camera-capture")
        self._camera_close = document.getElementById("camera-close")
        self._camera_stream = cast("JsVideoElement", document.getElementById("camera-stream"))
        self._camera_switch = document.getElementById("camera-switch")

        add_event_listener(self._camera_capture, "click", lambda _: self._handle_capture())
        add_event_listener(self._camera_close, "click", lambda _: self.destroy())
        add_event_listener(self._camera_switch, "click", lambda _: self._camera.toggle_facing_mode())

        self._subscription_is_acquiring_media_stream = self._camera.is_acquiring_media_stream.subscribe(
            lambda status: self._handle_is_acquiring_media_stream(status=status),
        )

        self._subscription_media_stream = self._camera.media_stream.subscribe(self._handle_media_stream)

        self._camera.acquire_media_stream()

    def _handle_capture(self) -> None:
        """Capture a snapshot from the camera stream."""
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

        canvas.toBlob(create_once_callable(self._handle_post_capture), "image/png")

    def _handle_is_acquiring_media_stream(self, *, status: bool) -> None:
        """Handle updates to the acquiring media stream status."""
        if status:
            self._camera_capture.classList.add("is-loading")
        else:
            self._camera_capture.classList.remove("is-loading")

    def _handle_media_stream(self, stream: Optional[MediaStream]) -> None:
        """Handle updates to the media stream."""
        self._camera_stream.srcObject = stream

        if not stream:
            self._camera_capture.setAttribute("disabled", "")
            self._camera_switch.setAttribute("disabled", "")
            self._camera_stream.classList.add("is-skeleton")
        else:
            self._camera_capture.removeAttribute("disabled")
            self._camera_switch.removeAttribute("disabled")
            self._camera_stream.classList.remove("is-skeleton")

    def _handle_post_capture(self, photo: Blob) -> None:
        """Download the captured photo."""
        url = URL.createObjectURL(photo)

        link = document.createElement("a")
        link.href = url
        link.download = "capture.png"
        link.click()

        URL.revokeObjectURL(url)
