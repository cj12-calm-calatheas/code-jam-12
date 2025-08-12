import logging
from typing import Literal, Optional, cast

from js import MediaStream, localStorage, navigator
from pyodide.webloop import PyodideFuture
from reactivex import Observable, Subject, empty
from reactivex import operators as op
from reactivex.subject import BehaviorSubject

FACING_MODES = {"user", "environment"}
LOCAL_STORAGE_KEY = "preferred_facing_mode"

type FacingMode = Literal["user", "environment"]


class Camera:
    """A service for accessing the user's camera."""

    camera_stream = BehaviorSubject[Optional[MediaStream]](value=None)
    is_acquiring_camera = BehaviorSubject[bool](value=False)

    _logger = logging.getLogger(__name__)
    _open = Subject[None]()

    def __init__(self) -> None:
        # Acquire the camera stream and notify subscribers when it's available
        self._open.pipe(
            op.do_action(lambda _: self.is_acquiring_camera.on_next(value=True)),
            op.map(lambda _: self._get_user_media().finally_(lambda: self.is_acquiring_camera.on_next(value=False))),
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
        if self._preferred_facing_mode == "user":
            self._preferred_facing_mode = "environment"
        else:
            self._preferred_facing_mode = "user"

        self.deactivate()
        self.open_camera()

    def _get_user_media(self) -> PyodideFuture[MediaStream]:
        """
        Get the user's media stream.

        Requests video access from the user. If access is not granted, a DOMException will be raised.
        """
        constraints = {"video": {"facingMode": self._preferred_facing_mode}}
        return navigator.mediaDevices.getUserMedia(constraints)

    def _handle_camera_stream_error(self, err: Exception) -> Observable:
        """Handle errors that occur while trying to access the camera."""
        self._logger.error("Error accessing camera", exc_info=err)
        return empty()

    @property
    def _preferred_facing_mode(self) -> FacingMode:
        """Return the preferred facing mode for the camera."""
        mode = localStorage.getItem(LOCAL_STORAGE_KEY)
        return cast("FacingMode", mode) if mode in FACING_MODES else "user"

    @_preferred_facing_mode.setter
    def _preferred_facing_mode(self, value: FacingMode) -> None:
        localStorage.setItem(LOCAL_STORAGE_KEY, value)


camera = Camera()
