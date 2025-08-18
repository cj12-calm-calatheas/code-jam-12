import logging
from asyncio import create_task

from reactivex import Observable, empty, from_future
from reactivex import operators as op
from reactivex.subject import BehaviorSubject, Subject

from frontend.models import PokemonRecord

from .database import database
from .description import description
from .reader import reader


class Pokemon:
    """Service that maintains a list of the user's current Pokemon."""

    is_refreshing = BehaviorSubject[bool](value=False)
    pokemon = BehaviorSubject[list[PokemonRecord]](value=[])

    _logger = logging.getLogger(__name__)

    _delete = Subject[str]()
    _favourite = Subject[str]()
    _refresh = Subject[None]()

    def __init__(self) -> None:
        # When a new description is available, do the following:
        # 1. Retrieve the corresponding image URL
        # 2. Create a new record and add it to the list
        # 3. Trigger a refresh
        description.descriptions.pipe(
            op.with_latest_from(reader.object_urls),
            op.map(lambda params: PokemonRecord(**params[0].model_dump(), img_url=params[1])),
            op.flat_map_latest(lambda pokemon: from_future(create_task(database.put(pokemon)))),
            op.catch(lambda err, _: self._handle_update_error(err)),
        ).subscribe(lambda _: self.refresh())

        # On delete, remove the Pokemon from the list and trigger a refresh
        self._delete.pipe(
            op.flat_map_latest(lambda name: from_future(create_task(database.delete(name)))),
            op.catch(lambda err, _: self._handle_delete_error(err)),
        ).subscribe(lambda _: self.refresh())

        # When the user clicks the "favourite button", toggle the
        # status of the pokemon in the database
        self._favourite.pipe(
            op.flat_map_latest(lambda name: from_future(create_task(database.favourite(name)))),
            op.catch(lambda err, _: self._handle_favourite_error(err)),
        ).subscribe(lambda _: self.refresh())

        # Retrieve the current list of Pokemon from the database
        self._refresh.pipe(
            op.do_action(lambda _: self.is_refreshing.on_next(value=True)),
            op.flat_map_latest(
                lambda _: from_future(create_task(database.find_all())).pipe(
                    op.finally_action(lambda: self.is_refreshing.on_next(value=False)),
                ),
            ),
            op.catch(lambda err, _: self._handle_refresh_error(err)),
        ).subscribe(self.pokemon)

        # Trigger a refresh on startup
        self.refresh()

    def delete(self, name: str) -> None:
        """Delete the pokemon with the given name."""
        self._delete.on_next(name)

    def favourite(self, name: str) -> None:
        """Mark a pokemon with the given name as a favourite."""
        self._favourite.on_next(name)

    def refresh(self) -> None:
        """Trigger a refresh of the descriptions."""
        self._refresh.on_next(None)

    def _handle_delete_error(self, err: Exception) -> Observable:
        self._logger.error("Failed to delete pokemon", exc_info=err)
        return empty()

    def _handle_favourite_error(self, err: Exception) -> Observable:
        self._logger.error("Failed to favourite pokemon", exc_info=err)
        return empty()

    def _handle_refresh_error(self, err: Exception) -> Observable:
        self._logger.error("Failed to refresh list of pokemon", exc_info=err)
        return empty()

    def _handle_update_error(self, err: Exception) -> Observable:
        self._logger.error("Failed to update pokemon", exc_info=err)
        return empty()


pokemon = Pokemon()
