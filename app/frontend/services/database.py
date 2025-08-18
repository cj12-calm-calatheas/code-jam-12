import asyncio
from typing import TYPE_CHECKING, override

from js import JSON, Event, console, indexedDB
from pyodide.ffi.wrappers import add_event_listener

from frontend.base import Service
from frontend.models import PokemonRecord

if TYPE_CHECKING:
    from js import IDBDatabase

_COLLECTION_NAME = "pokemon"
_DB_NAME = "calm_calatheas"
_DB_VERSION = 1
_READY = asyncio.Event()


class DatabaseNotInitializedError(Exception):
    """Error raised when the database is not initialized."""

    def __init__(self) -> None:
        super().__init__("Database is not initialized.")


class Database(Service):
    """Service for interacting with IndexedDB."""

    def __init__(self) -> None:
        super().__init__()

        self._db: IDBDatabase | None = None

        open_ = indexedDB.open(_DB_NAME, _DB_VERSION)

        add_event_listener(open_, "success", self._handle_open_success)
        add_event_listener(open_, "upgradeneeded", self._handle_open_upgrade_needed)

    @override
    def on_destroy(self) -> None:
        if self._db:
            self._db.close()

    async def delete(self, name: str) -> None:
        """Delete a Pokemon."""
        await _READY.wait()

        if not self._db:
            raise DatabaseNotInitializedError

        future = asyncio.Future[None]()

        transaction = self._db.transaction(_COLLECTION_NAME, "readwrite")
        store = transaction.objectStore(_COLLECTION_NAME)

        query = store.delete(name)

        def on_complete(_: Event) -> None:
            transaction.close()

        def on_error(_: Event) -> None:
            future.set_exception(Exception(f"Failed to delete pokemon {name}"))

        def on_success(_: Event) -> None:
            future.set_result(None)

        add_event_listener(query, "complete", on_complete)
        add_event_listener(query, "error", on_error)
        add_event_listener(query, "success", on_success)

        return await future

    async def find_all(self) -> list[PokemonRecord]:
        """Find all Pokemon."""
        await _READY.wait()

        if not self._db:
            raise DatabaseNotInitializedError

        future = asyncio.Future[list[PokemonRecord]]()

        transaction = self._db.transaction(_COLLECTION_NAME, "readonly")
        store = transaction.objectStore(_COLLECTION_NAME)

        query = store.getAll()

        def on_complete(_: Event) -> None:
            transaction.close()

        def on_error(_: Event) -> None:
            future.set_result([])

        def on_success(event: Event) -> None:
            # Some serialization and deserialization magic to ensure the data is accepted by Pydantic
            result = [
                PokemonRecord.model_validate_json(JSON.stringify(item))
                for item in event.target.result  # type: ignore[result is available]
            ]
            future.set_result(result)

        add_event_listener(query, "complete", on_complete)
        add_event_listener(query, "error", on_error)
        add_event_listener(query, "success", on_success)

        return await future

    async def find_one(self, name: str) -> PokemonRecord | None:
        """Find a single Pokemon."""
        await _READY.wait()

        if not self._db:
            raise DatabaseNotInitializedError

        future = asyncio.Future[PokemonRecord | None]()

        transaction = self._db.transaction(_COLLECTION_NAME, "readonly")
        store = transaction.objectStore(_COLLECTION_NAME)

        query = store.get(name)

        def on_complete(_: Event) -> None:
            transaction.close()

        def on_error(_: Event) -> None:
            future.set_result(None)

        def on_success(event: Event) -> None:
            # Some serialization and deserialization magic to ensure the data is accepted by Pydantic
            result = PokemonRecord.model_validate_json(JSON.stringify(event.target.result))  # type: ignore[result is available]
            future.set_result(result)

        add_event_listener(query, "complete", on_complete)
        add_event_listener(query, "error", on_error)
        add_event_listener(query, "success", on_success)

        return await future

    async def put(self, description: PokemonRecord) -> None:
        """Store a Pokemon."""
        await _READY.wait()

        if not self._db:
            raise DatabaseNotInitializedError

        future = asyncio.Future[None]()

        transaction = self._db.transaction(_COLLECTION_NAME, "readwrite")
        store = transaction.objectStore(_COLLECTION_NAME)

        # Some serialization and deserialization magic to ensure the data is accepted by IndexedDB
        query = store.put(JSON.parse(description.model_dump_json()))

        def on_complete(_: Event) -> None:
            transaction.close()

        def on_error(_: Event) -> None:
            future.set_exception(Exception(f"Failed to store pokemon {description.name}"))

        def on_success(_: Event) -> None:
            future.set_result(None)

        add_event_listener(query, "complete", on_complete)
        add_event_listener(query, "error", on_error)
        add_event_listener(query, "success", on_success)

        return await future

    def _handle_open_success(self, event: Event) -> None:
        """Handle the successful opening of the database."""
        self._db = event.target.result  # type: ignore[result is available]
        console.log("Opened IndexedDB.")

        _READY.set()

    def _handle_open_upgrade_needed(self, event: Event) -> None:
        """Handle the upgrade needed event."""
        self._db = event.target.result  # type: ignore[result is available]

        if not self._db:
            raise DatabaseNotInitializedError

        self._db.createObjectStore(_COLLECTION_NAME, {"keyPath": "name"})

        add_event_listener(event.target.transaction, "complete", self._handle_upgrade_transaction_complete)  # type: ignore[transaction is available]

    def _handle_upgrade_transaction_complete(self, _: Event) -> None:
        """Handle the completion of the upgrade transaction."""
        console.log("Initialized IndexedDB.")
        _READY.set()


database = Database()
