import logging
from asyncio import Future
from typing import Union

from js import Blob, File, FileReader
from pyodide.ffi.wrappers import add_event_listener
from reactivex import Observable, empty, from_future
from reactivex import operators as op
from reactivex.subject import BehaviorSubject, ReplaySubject, Subject

type Readable = Union[Blob, File]


class Reader:
    """Service for reading files and generating object URLs."""

    is_reading = BehaviorSubject[bool](value=False)
    object_urls = ReplaySubject[str]()

    _files = Subject[Readable]()
    _logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._files.pipe(
            op.do_action(lambda _: self.is_reading.on_next(value=True)),
            op.flat_map_latest(
                lambda file: from_future(self._read_file(file)).pipe(
                    op.finally_action(lambda: self.is_reading.on_next(value=False)),
                ),
            ),
            op.catch(lambda err, _: self._handle_reader_error(err)),
        ).subscribe(self.object_urls)

        self.object_urls.subscribe(print)

    def destroy(self) -> None:
        """Clean up resources used by the reader."""
        self._files.dispose()
        self.is_reading.dispose()
        self.object_urls.dispose()

    def read(self, file: Readable) -> None:
        """Upload a file and trigger further processing."""
        self._files.on_next(file)

    def _handle_reader_error(self, err: Exception) -> Observable:
        """Handle errors that occur while reading files."""
        self._logger.error("Error reading file", exc_info=err)
        return empty()

    def _read_file(self, file: Readable) -> Future[str]:
        """Read a file and return its object URL."""
        result = Future()

        reader = FileReader.new()  # type: ignore[new method is unknown]

        add_event_listener(reader, "load", lambda _: result.set_result(reader.result))
        add_event_listener(reader, "error", lambda e: result.set_exception(e))

        reader.readAsDataURL(file)

        return result


reader = Reader()
