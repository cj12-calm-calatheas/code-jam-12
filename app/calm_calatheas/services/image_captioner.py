import asyncio
import time
from typing import ClassVar

from js import console, pipeline

MODEL_NAME = "Xenova/vit-gpt2-image-captioning"


class ModelNotLoadedError(Exception):
    """Error to signal that the model has not yet been loaded."""


class ImageCaptioner:
    """Service to caption images."""

    _options: ClassVar[dict] = {"dtype": "q8", "device": "wasm"}

    def __init__(self) -> None:
        self._model_loaded = False

        asyncio.create_task(self.initialize_model())

    async def initialize_model(self) -> None:
        """Load the model asynchronously when the app loads."""
        console.log("Loading description model...")
        t0 = time.time()
        self._model = await pipeline("image-to-text", MODEL_NAME, self._options)
        console.log("Description model loaded!")
        console.log(time.time() - t0)

        self._model_loaded = True

    async def caption(self, url: str) -> str:
        """Generate a caption for an image."""
        if not self._model_loaded:
            raise ModelNotLoadedError

        console.log("Generating description...")
        output = await self._model(url)
        console.log("Description generated!")
        return output.at(0).generated_text


image_captioner = ImageCaptioner()
