from typing import Optional, override

from js import URL, Blob, MediaStream, document
from pyodide.ffi import JsDomElement, create_once_callable
from pyodide.ffi.wrappers import add_event_listener

from calm_calatheas.base import Component
from calm_calatheas.services import camera

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
        self._subscription_acquiring_stream.dispose()
        self._subscription_camera_stream.dispose()
        self._camera.deactivate()

    @override
    def on_render(self) -> None:
        self._camera_capture = document.getElementById("camera-capture")
        self._camera_close = document.getElementById("camera-close")
        self._camera_stream = document.getElementById("camera-stream")
        self._camera_switch = document.getElementById("camera-switch")

        add_event_listener(self._camera_capture, "click", lambda _: self._handle_capture())
        add_event_listener(self._camera_close, "click", lambda _: self.destroy())
        add_event_listener(self._camera_switch, "click", lambda _: self._camera.switch_facing_mode())

        self._subscription_acquiring_stream = self._camera.is_acquiring_camera.subscribe(
            lambda status: self._handle_acquiring_stream(status=status),
        )

        self._subscription_camera_stream = self._camera.camera_stream.subscribe(self._handle_update_stream)

        self._camera.open_camera()

    def _handle_capture(self) -> None:
        """Handle the capture action."""
        canvas = document.createElement("canvas")
        canvas.width = self._camera_stream.videoWidth  # type: ignore[videoWidth is present]
        canvas.height = self._camera_stream.videoHeight  # type: ignore[videoHeight is present]

        context = canvas.getContext("2d")

        context.drawImage(
            self._camera_stream,  # type: ignore[video element is allowed]
            0,
            0,
            self._camera_stream.videoWidth,  # type: ignore[videoWidth is present]
            self._camera_stream.videoHeight,  # type: ignore[videoHeight is present]
        )

        canvas.toBlob(create_once_callable(self._handle_post_capture), "image/png")

    def _handle_acquiring_stream(self, *, status: bool) -> None:
        """Handle the acquiring camera status."""
        if status:
            self._camera_capture.classList.add("is-loading")
        else:
            self._camera_capture.classList.remove("is-loading")

    def _handle_update_stream(self, stream: Optional[MediaStream]) -> None:
        """Handle updates to the media stream."""
        if not stream:
            self._camera_capture.setAttribute("disabled", "")
            self._camera_switch.setAttribute("disabled", "")
        else:
            self._camera_capture.removeAttribute("disabled")
            self._camera_switch.removeAttribute("disabled")

        self._camera_stream.srcObject = stream  # type: ignore[srcObject attribute is available]

    def _handle_post_capture(self, photo: Blob) -> None:
        """Handle the creation of an object URL for the captured photo."""
        url = URL.createObjectURL(photo)

        link = document.createElement("a")
        link.href = url
        link.download = "capture.png"
        link.click()

        URL.revokeObjectURL(url)
