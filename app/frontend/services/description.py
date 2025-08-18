import logging
from asyncio import create_task

from pyodide.http import pyfetch
from reactivex import Observable, empty, from_future
from reactivex import operators as op
from reactivex.subject import BehaviorSubject, ReplaySubject

from frontend.models import PokemonDescription

from .caption import caption


class Description:
    """Service to generate descriptions from captions."""

    is_generating_description = BehaviorSubject[bool](value=False)
    descriptions = ReplaySubject[PokemonDescription]()

    _logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        # Generate descriptions when an image is available and the model is loaded, and notify subscribers when done
        caption.captions.pipe(
            op.do_action(lambda _: self.is_generating_description.on_next(value=True)),
            op.flat_map_latest(
                lambda caption: from_future(create_task(self._describe(caption))).pipe(
                    op.finally_action(
                        lambda: self.is_generating_description.on_next(value=False),
                    ),
                ),
            ),
            op.catch(lambda err, _: self._handle_description_error(err)),
        ).subscribe(self.descriptions)

    async def _describe(self, caption: str) -> PokemonDescription:
        """Generate a description from the given caption."""
        self._logger.debug("Generating description for caption: %s", caption)

        response = await pyfetch(f"/describe?prompt={caption}")

        response.raise_for_status()

        data = await response.json()

        self._logger.debug("Generated description: %s", data)

        return PokemonDescription.model_validate(data)

    def _handle_description_error(self, err: Exception) -> Observable:
        self._logger.error("Failed to generate description", exc_info=err)
        return empty()


description = Description()
