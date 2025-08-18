from asyncio import Future
from typing import Union, override

from js import Blob, File, FileReader, console
from pyodide.ffi.wrappers import add_event_listener
from reactivex import Observable, empty, from_future
from reactivex import operators as op
from reactivex.subject import BehaviorSubject, ReplaySubject, Subject

from frontend.base import Service

type Readable = Union[Blob, File]


class Reader(Service):
    """Service for reading files and generating object URLs."""

    def __init__(self) -> None:
        super().__init__()

        self.is_reading = BehaviorSubject[bool](value=False)
        self.object_urls = ReplaySubject[str]()

        self._read = Subject[Readable]()

        # On read, generate an object URL for the object
        self._read.pipe(
            op.do_action(lambda _: self.is_reading.on_next(value=True)),
            op.flat_map_latest(
                lambda file_: from_future(self._generate_object_url(file_)).pipe(
                    op.finally_action(lambda: self.is_reading.on_next(value=False)),
                ),
            ),
            op.catch(lambda err, _: self._handle_reader_error(err)),
            op.take_until(self.destroyed),
        ).subscribe(self.object_urls)

    @override
    def on_destroy(self) -> None:
        self._read.dispose()
        self.is_reading.dispose()
        self.object_urls.dispose()

    def read(self, object_: Readable) -> None:
        """Upload an object and trigger further processing."""
        self._read.on_next(object_)

    def _handle_reader_error(self, err: Exception) -> Observable:
        """Handle errors that occur while reading objects."""
        console.error("Error reading object:", err)
        return empty()

    def _generate_object_url(self, object_: Readable) -> Future[str]:
        """Read an object and return its object URL."""
        result = Future()

        reader = FileReader.new()

        add_event_listener(reader, "load", lambda _: result.set_result(reader.result))  # type: ignore[FileReader also supported]
        add_event_listener(reader, "error", lambda e: result.set_exception(e))  # type: ignore[FileReader also supported]

        reader.readAsDataURL(object_)

        return result


reader = Reader()
