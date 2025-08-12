import logging
from typing import Optional

from js import MediaStream, navigator
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
        """Deactivates the camera."""
        if not (camera_stream := self.camera_stream.value):
            self._logger.warning("Camera is not active, nothing to deactivate")
            return

        for track in camera_stream.getTracks():
            track.stop()

        self.camera_stream.on_next(None)

    def destroy(self) -> None:
        """Cleans up the camera resources."""
        self.deactivate()
        self._open.dispose()
        self.camera_stream.dispose()

    def open_camera(self) -> None:
        """Triggers the process of opening the camera."""
        if self.camera_stream.value:
            self._logger.warning("Camera is already open")
            return

        self._open.on_next(None)

    def _get_user_media(self) -> PyodideFuture[MediaStream]:
        """
        Get the user's media stream.

        Requests video access from the user. If access is not granted, a DOMException will be raised.
        """
        constraints = {"video": True}
        return navigator.mediaDevices.getUserMedia(constraints)

    def _handle_camera_stream_error(self, err: Exception) -> Observable:
        """Handles errors that occur while trying to access the camera."""
        self._logger.error("Error accessing camera", exc_info=err)
        return empty()


camera = Camera()
