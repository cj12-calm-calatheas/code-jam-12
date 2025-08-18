from asyncio import Future, create_task
from collections.abc import Callable
from typing import TYPE_CHECKING

from js import console, window
from reactivex import Observable, combine_latest, empty, from_future, of
from reactivex import operators as op
from reactivex.subject import BehaviorSubject, ReplaySubject

from .reader import reader

if TYPE_CHECKING:
    from transformers_js import ModelOutput

type Model = Callable[[str], Future[ModelOutput]]

MODEL_NAME = "Xenova/vit-gpt2-image-captioning"


class Caption:
    """Service to generate captions for images."""

    def __init__(self) -> None:
        self.captions = ReplaySubject[str]()
        self.model = ReplaySubject[Model]()

        self.is_generating_caption = BehaviorSubject[bool](value=False)
        self.is_loading_model = BehaviorSubject[bool](value=False)

        # Load the model and notify subscribers when it's ready
        of(MODEL_NAME).pipe(
            op.do_action(lambda _: self.is_loading_model.on_next(value=True)),
            op.flat_map_latest(
                lambda model_name: from_future(
                    create_task(self._load_model(model_name)),
                ).pipe(
                    op.finally_action(
                        lambda: self.is_loading_model.on_next(value=False),
                    ),
                ),
            ),
            op.catch(lambda err, _: self._handle_load_model_error(err)),
        ).subscribe(self.model)

        # Generate captions when an image is available and the model is loaded, and notify subscribers when done
        combine_latest(reader.object_urls, self.model).pipe(
            op.do_action(lambda _: self.is_generating_caption.on_next(value=True)),
            op.flat_map_latest(
                lambda params: from_future(create_task(self._caption(*params))).pipe(
                    op.finally_action(
                        lambda: self.is_generating_caption.on_next(value=False),
                    ),
                ),
            ),
            op.catch(lambda err, _: self._handle_caption_error(err)),
        ).subscribe(self.captions)

    async def _caption(self, url: str, model: Model) -> str:
        """Generate a caption for the image at the given URL."""
        output = await model(url)
        return output.at(0).generated_text

    def _handle_caption_error(self, err: Exception) -> Observable:
        console.error("Failed to generate caption:", err)
        return empty()

    def _handle_load_model_error(self, err: Exception) -> Observable:
        console.error("Failed to load model:", err)
        return empty()

    async def _load_model(self, model_name: str) -> Model:
        """Load the given model."""
        return await window.pipeline(
            "image-to-text",
            model_name,
            {"dtype": "q8", "device": "wasm"},
        )


caption = Caption()
