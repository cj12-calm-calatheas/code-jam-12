from asyncio import create_task
from typing import override

from js import console
from reactivex import Observable, combine_latest, empty, from_future
from reactivex import operators as op
from reactivex.subject import BehaviorSubject, Subject

from frontend.base import Service
from frontend.models import PokemonRecord

from .caption import caption
from .database import database
from .description import description
from .reader import reader


class Pokemon(Service):
    """Service that maintains a list of the user's current Pokemon."""

    def __init__(self) -> None:
        super().__init__()

        self.is_generating = BehaviorSubject[bool](value=False)
        self.is_refreshing = BehaviorSubject[bool](value=False)
        self.pokemon = BehaviorSubject[list[PokemonRecord]](value=[])

        self._delete = Subject[str]()
        self._put = Subject[PokemonRecord]()
        self._favourite = Subject[str]()
        self._refresh = Subject[None]()

        # Combine the loading states from all relevant sources
        combine_latest(
            caption.is_generating_caption,
            description.is_generating_description,
            reader.is_reading,
        ).pipe(
            op.map(lambda is_loading: any(is_loading)),
            op.distinct_until_changed(),
            op.take_until(self.destroyed),
        ).subscribe(self.is_generating)

        # Whenever a new description is available, get the corresponding image url and create an new database record
        description.descriptions.pipe(
            op.with_latest_from(reader.object_urls),
            op.map(lambda params: PokemonRecord(**params[0].model_dump(), img_url=params[1])),
            op.take_until(self.destroyed),
        ).subscribe(self._put)

        # On put, update the database with the given record
        self._put.pipe(
            op.flat_map_latest(lambda pokemon: from_future(create_task(database.put(pokemon)))),
            op.catch(lambda err, _: self._handle_update_error(err)),
            op.take_until(self.destroyed),
        ).subscribe(lambda _: self.refresh())

        # On delete, remove the Pokemon from the list and trigger a refresh
        self._delete.pipe(
            op.flat_map_latest(lambda name: from_future(create_task(database.delete(name)))),
            op.catch(lambda err, _: self._handle_delete_error(err)),
            op.take_until(self.destroyed),
        ).subscribe(lambda _: self.refresh())

        # Retrieve the current list of Pokemon from the database
        # On refresh, retrieve the current list of Pokemon from the database. Sort the list by timestamp
        self._refresh.pipe(
            op.do_action(lambda _: self.is_refreshing.on_next(value=True)),
            op.flat_map_latest(
                lambda _: from_future(create_task(database.find_all())).pipe(
                    op.finally_action(lambda: self.is_refreshing.on_next(value=False)),
                ),
            ),
            op.catch(lambda err, _: self._handle_refresh_error(err)),
            op.map(lambda pokemon: sorted(pokemon, key=lambda p: p.timestamp, reverse=True)),
            op.take_until(self.destroyed),
        ).subscribe(self.pokemon)

        # Trigger a refresh on startup
        self.refresh()

    @override
    def on_destroy(self) -> None:
        self.is_generating.dispose()
        self.is_refreshing.dispose()
        self.pokemon.dispose()
        self._delete.dispose()
        self._put.dispose()
        self._refresh.dispose()

    def delete(self, name: str) -> None:
        """Delete the pokemon with the given name."""
        self._delete.on_next(name)

    def put(self, pokemon: PokemonRecord) -> None:
        """Update the database with the given pokemon."""
        self._put.on_next(pokemon)

    def refresh(self) -> None:
        """Trigger a refresh of the list."""
        self._refresh.on_next(None)

    def _handle_delete_error(self, err: Exception) -> Observable:
        """Handle errors that occur while deleting a Pokemon."""
        console.error("Failed to delete pokemon:", err)
        return empty()

    def _handle_favourite_error(self, err: Exception) -> Observable:
        console.error("Failed to favourite pokemon", err)
        return empty()

    def _handle_refresh_error(self, err: Exception) -> Observable:
        """Handle errors that occur while refreshing the list of Pokemon."""
        console.error("Failed to refresh list of pokemon:", err)
        return empty()

    def _handle_update_error(self, err: Exception) -> Observable:
        """Handle errors that occur while updating a Pokemon."""
        console.error("Failed to update pokemon:", err)
        return empty()


pokemon = Pokemon()
