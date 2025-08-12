import logging
from typing import Optional

from js import URL, Blob, ImageCapture, MediaStream, navigator
from pyodide.webloop import PyodideFuture
from reactivex import Observable, Subject, empty, from_future
from reactivex import operators as op
from reactivex.subject import BehaviorSubject, ReplaySubject


class Camera:
    """A service for accessing the user's camera."""

    camera_stream = BehaviorSubject[Optional[MediaStream]](None)
    captures = ReplaySubject[str]()

    _capture = Subject[None]()
    _logger = logging.getLogger(__name__)
    _open = Subject[None]()

    def __init__(self) -> None:
        # Acquire the camera stream and notify subscribers when it's available
        self._open.pipe(
            op.map(lambda _: self._get_user_media()),
            op.switch_latest(),
            op.catch(lambda err, _: self._handle_camera_stream_error(err)),
        ).subscribe(self.camera_stream)

        # Capture an image from the current stream and transform it to an object URL
        self._capture.pipe(
            op.map(lambda _: self._handle_capture()),
            op.switch_latest(),
            op.catch(lambda err, _: self._handle_capture_error(err)),
            op.map(lambda photo: self._handle_create_object_url(photo)),
        ).subscribe(self.captures)

    def capture(self) -> None:
        """Triggers the photo capture process."""
        self._capture.on_next(None)

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
        self._capture.dispose()
        self._open.dispose()
        self.captures.dispose()
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

    def _handle_capture_error(self, err: Exception) -> Observable:
        self._logger.error("Error taking photo", exc_info=err)
        return empty()

    def _handle_capture(self) -> Observable[Blob]:
        if not (stream := self.camera_stream.value):
            return empty()

        video_tracks = stream.getVideoTracks()

        if not len(video_tracks):
            return empty()

        image_capture: ImageCapture = ImageCapture.new(video_tracks[0])  # type: ignore[]

        return from_future(image_capture.takePhoto())

    def _handle_camera_stream_error(self, err: Exception) -> Observable:
        """Handles errors that occur while trying to access the camera."""
        self._logger.error("Error accessing camera", exc_info=err)
        return empty()

    def _handle_create_object_url(self, blob: Blob) -> str:
        """Creates an object URL from a Blob."""
        return URL.createObjectURL(blob)


camera = Camera()
