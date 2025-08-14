import logging
from asyncio import Future, create_task
from collections.abc import Callable
from typing import TYPE_CHECKING

from js import window
from reactivex import Observable, combine_latest, empty, from_future, of
from reactivex import operators as op
from reactivex.subject import BehaviorSubject, ReplaySubject

from .caption import caption

if TYPE_CHECKING:
    from transformers_js import ModelOutput

type Model = Callable[[str], Future[ModelOutput]]

MODEL_NAME = "onnx-community/LFM2-1.2B-ONNX"

CONTEXT = """
You are a Pokemon professor. You will be given a caption and must generate a corresponding Pokedex entry.
The generated text should include the Pokemon's name, type, and a flavour text.
"""

QUESTION_TEMPLATE = """
{caption}
"""


class Description:
    """Service to generate descriptions from captions."""

    descriptions = ReplaySubject[str]()
    model = ReplaySubject[Model]()

    is_generating_description = BehaviorSubject[bool](value=False)
    is_loading_model = BehaviorSubject[bool](value=False)

    _logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._caption = caption

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
        combine_latest(self._caption.captions, self.model).pipe(
            op.do_action(lambda _: self.is_generating_description.on_next(value=True)),
            op.flat_map_latest(
                lambda params: from_future(create_task(self._describe(*params))).pipe(
                    op.finally_action(lambda: self.is_generating_description.on_next(value=False)),
                ),
            ),
            op.catch(lambda err, _: self._handle_description_error(err)),
        ).subscribe(self.descriptions)

    async def _describe(self, caption: str, model: Model) -> str:
        """Generate a description from the given caption."""
        model_input = "\n".join([CONTEXT, QUESTION_TEMPLATE.format(caption=caption)])
        output = await model(model_input)
        return output.at(0).generated_text

    def _handle_description_error(self, err: Exception) -> Observable:
        self._logger.error("Failed to generate description", exc_info=err)
        return empty()

    def _handle_load_model_error(self, err: Exception) -> Observable:
        self._logger.error("Failed to load model", exc_info=err)
        return empty()

    async def _load_model(self, model_name: str) -> Model:
        """Load the given model."""
        return await window.pipeline("text-generation", model_name, {"dtype": "q4", "device": "wasm"})


description = Description()
