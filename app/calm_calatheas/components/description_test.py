from collections.abc import Callable
from typing import Any, cast, override

import js
from js import Event, FileReader, console, document, window
from pyodide.ffi.wrappers import add_event_listener

from calm_calatheas.base import Component
from calm_calatheas.services import ModelNotLoadedError, image_captioner

TEMPLATE = """
<div>
    <div class="file">
        <label class="file-label has-name">
            <input id="file-input" class="file-input" type="file" name="file" />
            <span class="file-cta">
                <span class="file-icon">
                    <i class="fas fa-upload"></i>
                </span>
                <span class="file-label"> Choose a file… </span>
            </span>
            <span id="file-name" class="file-name">None selected</span>
        </label>
    </div>
    <button id="submit" class="button is-large is-primary">Generate description!</button>
    <p id="caption"></p>
</div>
"""


class DescriptionTest(Component):
    """Test component to demonstrate the descriptions service."""

    @override
    def build(self) -> str:
        return TEMPLATE

    @override
    def on_render(self) -> None:
        self._file_input = cast("js.JsFileInputElement", document.getElementById("file-input"))
        self._file_name = document.getElementById("file-name")
        self._caption = document.getElementById("caption")
        self._button = document.getElementById("submit")

        add_event_listener(self._file_input, "change", self._change_file)
        add_event_listener(self._button, "click", self._generate_description)  # type: ignore[callbacks can be async]

    def _change_file(self, _: Event) -> None:
        if self._file_input.files.length == 1:
            self._file_name.innerText = self._file_input.files.item(0).name
        else:
            self._file_name.innerText = "None selected"

    async def _generate_description(self, _: Event) -> None:
        if self._file_input.files.length != 1:
            return

        file = self._file_input.files.item(0)
        reader = FileReader.new()

        def _promise(resolve: Callable[[Any], None], reject: Callable[[Any], None]) -> None:
            reader.onload = lambda _: resolve(reader.result)
            reader.onerror = lambda error: reject(error)

            reader.readAsDataURL(file)

        data_url = await window.Promise.new(_promise)
        try:
            generated_caption = await image_captioner.caption(data_url)
            self._caption.innerText = generated_caption
        except ModelNotLoadedError:
            console.error("Model not loaded!")
