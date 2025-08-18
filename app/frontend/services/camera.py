from typing import Literal, Optional, cast

from js import MediaStream, console, localStorage, navigator
from pyodide.webloop import PyodideFuture
from reactivex import Observable, Subject, empty
from reactivex import operators as op
from reactivex.subject import BehaviorSubject

FACING_MODES = {"user", "environment"}
LOCAL_STORAGE_KEY = "preferred_facing_mode"

type FacingMode = Literal["user", "environment"]


class Camera:
    """A service for accessing the user's camera."""

    def __init__(self) -> None:
        self.media_stream = BehaviorSubject[Optional[MediaStream]](value=None)
        self.is_acquiring_media_stream = BehaviorSubject[bool](value=False)

        self._acquire = Subject[None]()

        # Acquire the media stream and notify subscribers when it's available
        self._acquire.pipe(
            op.do_action(lambda _: self.is_acquiring_media_stream.on_next(value=True)),
            op.flat_map_latest(
                lambda _: self._acquire_media_stream().finally_(
                    lambda: self.is_acquiring_media_stream.on_next(value=False),
                ),
            ),
            op.catch(lambda err, _: self._handle_acquisition_error(err)),
        ).subscribe(self.media_stream)

    def dispose_media_stream(self) -> None:
        """Stop all tracks in the media stream and notify subscribers."""
        if not (camera_stream := self.media_stream.value):
            return

        for track in camera_stream.getTracks():
            track.stop()

        self.media_stream.on_next(None)

    def destroy(self) -> None:
        """Clean up the camera resources."""
        self.dispose_media_stream()
        self._acquire.dispose()
        self.media_stream.dispose()

    def acquire_media_stream(self) -> None:
        """Trigger the process of acquiring the media stream."""
        if self.media_stream.value:
            return
        self._acquire.on_next(None)

    def toggle_facing_mode(self) -> None:
        """Switch the preferred facing mode between user and environment."""
        if self._preferred_facing_mode == "user":
            self._preferred_facing_mode = "environment"
        else:
            self._preferred_facing_mode = "user"

        self.dispose_media_stream()
        self.acquire_media_stream()

    def _acquire_media_stream(self) -> PyodideFuture[MediaStream]:
        """
        Get the user's media stream.

        Requests video access from the user. If access is not granted, a DOMException will be raised.
        """
        constraints = {"video": {"facingMode": self._preferred_facing_mode}}
        return navigator.mediaDevices.getUserMedia(constraints)

    def _handle_acquisition_error(self, err: Exception) -> Observable:
        """Handle errors that occur while acquiring the media stream."""
        console.error("Error acquiring media stream:", err)
        return empty()

    @property
    def _preferred_facing_mode(self) -> FacingMode:
        """
        Return the preferred facing mode for the camera.

        Save the user preference in local storage to ensure it persists across sessions.
        """
        mode = localStorage.getItem(LOCAL_STORAGE_KEY)
        return cast("FacingMode", mode) if mode in FACING_MODES else "user"

    @_preferred_facing_mode.setter
    def _preferred_facing_mode(self, value: FacingMode) -> None:
        localStorage.setItem(LOCAL_STORAGE_KEY, value)
