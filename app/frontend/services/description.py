from asyncio import create_task

from js import console
from pyodide.http import pyfetch
from reactivex import Observable, empty, from_future
from reactivex import operators as op
from reactivex.subject import BehaviorSubject, ReplaySubject

from frontend.base import Service
from frontend.models import PokemonDescription

from .caption import caption


class Description(Service):
    """Service to generate descriptions from captions."""

    def __init__(self) -> None:
        super().__init__()

        self.is_generating_description = BehaviorSubject[bool](value=False)
        self.descriptions = ReplaySubject[PokemonDescription]()

        # Generate descriptions whenever a new caption is available
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
            op.take_until(self.destroyed),
        ).subscribe(self.descriptions)

    async def _describe(self, caption: str) -> PokemonDescription:
        """Generate a description from the given caption."""
        console.log("Generating description for caption:", caption)

        response = await pyfetch(f"/describe?prompt={caption}")
        response.raise_for_status()

        data = await response.json()
        description = PokemonDescription.model_validate(data)

        console.log("Generated description:", description.model_dump_json())

        return description

    def _handle_description_error(self, err: Exception) -> Observable:
        """Handle errors that occur while generating descriptions."""
        console.error("Failed to generate description:", err)
        return empty()


description = Description()
