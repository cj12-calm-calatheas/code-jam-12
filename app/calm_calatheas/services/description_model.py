import asyncio
from typing import ClassVar

from js import console, pipeline  # type: ignore[TOADD]

MODEL_NAME = "Xenova/vit-gpt2-image-captioning"


class DescriptionModel:
    """Service to describe images."""

    _options: ClassVar[dict] = {"dtype": "q8", "device": "wasm"}

    def __init__(self) -> None:
        self._model_loaded = False

        asyncio.create_task(self.initialize_model())

    async def initialize_model(self) -> None:
        """Load the model asynchronously when the app loads."""
        console.log("Loading description model...")
        self._model = await pipeline("image-to-text", MODEL_NAME, self._options)
        console.log("Description model loaded!")

        self._model_loaded = True

    async def caption(self, url: str) -> str | None:
        """Generate a caption for an image."""
        if self._model_loaded:
            console.log("Generating description...")
            output = await self._model(url)
            console.log("Description generated!")
            return output.at(0).generated_text

        return None  # or raise an exception?


description_model = DescriptionModel()
