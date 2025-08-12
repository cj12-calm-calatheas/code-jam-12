import logging
from typing import Optional

from js import MediaStream, localStorage, navigator
from pyodide.webloop import PyodideFuture
from reactivex import Observable, Subject, empty
from reactivex import operators as op
from reactivex.subject import BehaviorSubject


class Camera:
    """A service for accessing the user's camera."""

    camera_stream = BehaviorSubject[Optional[MediaStream]](None)

    _logger = logging.getLogger(__name__)
    _open = Subject[None]()

    def __init__(self) -> None:
        # Acquire the camera stream and notify subscribers when it's available
        self._open.pipe(
            op.map(lambda _: self._get_user_media()),
            op.switch_latest(),
            op.catch(lambda err, _: self._handle_camera_stream_error(err)),
        ).subscribe(self.camera_stream)

    def deactivate(self) -> None:
        """Deactivate the camera."""
        if not (camera_stream := self.camera_stream.value):
            self._logger.warning("Camera is not active, nothing to deactivate")
            return

        for track in camera_stream.getTracks():
            track.stop()

        self.camera_stream.on_next(None)

    def destroy(self) -> None:
        """Clean up the camera resources."""
        self.deactivate()
        self._open.dispose()
        self.camera_stream.dispose()

    def open_camera(self) -> None:
        """Trigger the process of opening the camera."""
        if self.camera_stream.value:
            self._logger.warning("Camera is already open")
            return

        self._open.on_next(None)

    def switch_facing_mode(self) -> None:
        """Switch the preferred facing mode between user and environment."""
        if self.preferred_facing_mode == "user":
            self.preferred_facing_mode = "environment"
        else:
            self.preferred_facing_mode = "user"

        self.deactivate()
        self.open_camera()

    def _get_user_media(self) -> PyodideFuture[MediaStream]:
        """
        Get the user's media stream.

        Requests video access from the user. If access is not granted, a DOMException will be raised.
        """
        constraints = {"video": {"facingMode": self.preferred_facing_mode}}
        return navigator.mediaDevices.getUserMedia(constraints)

    def _handle_camera_stream_error(self, err: Exception) -> Observable:
        """Handle errors that occur while trying to access the camera."""
        self._logger.error("Error accessing camera", exc_info=err)
        return empty()

    @property
    def preferred_facing_mode(self) -> str:
        """Return the preferred facing mode for the camera."""
        return localStorage.getItem("preferred_facing_mode") or "user"

    @preferred_facing_mode.setter
    def preferred_facing_mode(self, value: str) -> None:
        localStorage.setItem("preferred_facing_mode", value)


camera = Camera()
