import logging
from asyncio import Future, create_task
from collections.abc import Callable
from typing import TYPE_CHECKING

from js import window
from reactivex import Observable, combine_latest, empty, from_future, of
from reactivex import operators as op
from reactivex.subject import BehaviorSubject, ReplaySubject

from .reader import reader

if TYPE_CHECKING:
    from transformers_js import ModelOutput

type Model = Callable[[str], Future[ModelOutput]]

MODEL_NAME = "Xenova/vit-gpt2-image-captioning"


class Description:
    """Service to generate descriptions of images."""

    descriptions = ReplaySubject[str]()
    model = ReplaySubject[Model]()

    is_generating = BehaviorSubject[bool](value=False)
    is_loading_model = BehaviorSubject[bool](value=False)

    _logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._reader = reader

        # Load the model and notify subscribers when it's ready
        of(MODEL_NAME).pipe(
            op.do_action(lambda _: self.is_loading_model.on_next(value=True)),
            op.flat_map_latest(
                lambda model_name: from_future(create_task(self._load_model(model_name))).pipe(
                    op.finally_action(lambda: self.is_loading_model.on_next(value=False)),
                ),
            ),
            op.catch(lambda err, _: self._handle_load_model_error(err)),
        ).subscribe(self.model)

        # Generate descriptions when an image is available and the model is loaded, and notify subscribers when done
        combine_latest(self._reader.object_urls, self.model).pipe(
            op.do_action(lambda _: self.is_generating.on_next(value=True)),
            op.flat_map_latest(
                lambda params: from_future(create_task(self._describe(*params))).pipe(
                    op.finally_action(lambda: self.is_generating.on_next(value=False)),
                ),
            ),
            op.catch(lambda err, _: self._handle_describe_error(err)),
        ).subscribe(self.descriptions)

    async def _describe(self, url: str, model: Model) -> str:
        """Generate a description for the image at the given URL."""
        output = await model(url)
        return output.at(0).generated_text

    def _handle_describe_error(self, err: Exception) -> Observable:
        self._logger.error("Failed to generate description", exc_info=err)
        return empty()

    def _handle_load_model_error(self, err: Exception) -> Observable:
        self._logger.error("Failed to load model", exc_info=err)
        return empty()

    async def _load_model(self, model_name: str) -> Model:
        """Load the given model."""
        return await window.pipeline("image-to-text", model_name, {"dtype": "q8", "device": "wasm"})


description = Description()
