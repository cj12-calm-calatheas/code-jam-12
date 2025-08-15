from typing import TYPE_CHECKING, cast, override

import reactivex.operators as op
from js import document
from pyodide.ffi import JsDomElement
from reactivex import combine_latest

from calm_calatheas.base import Component
from calm_calatheas.services import caption, reader

if TYPE_CHECKING:
    from js import JsImgElement

TEMPLATE = """
<article class="media">
  <figure class="media-left">
    <p id="description-image-container" class="image is-128x128">
      <img id="description-image" />
    </p>
  </figure>
  <div class="media-content">
    <div id="description-content" class="content"></div>
  </div>
</article>
"""


class Description(Component):
    """Test component to demonstrate the descriptions service."""

    def __init__(self, root: JsDomElement) -> None:
        super().__init__(root)
        self._caption = caption
        self._reader = reader

        self._is_loading = combine_latest(
            self._caption.is_generating_caption,
            self._reader.is_reading,
        ).pipe(op.map(lambda is_loading: any(is_loading)))

    @override
    def build(self) -> str:
        return TEMPLATE

    @override
    def on_destroy(self) -> None:
        self._subscription_descriptions.dispose()
        self._subscription_is_generating.dispose()

    @override
    def on_render(self) -> None:
        self._content = document.getElementById("description-content")
        self._image = cast("JsImgElement", document.getElementById("description-image"))
        self._image_container = document.getElementById("description-image-container")

        self._subscription_descriptions = self._caption.captions.subscribe(
            lambda caption: self._handle_description_update(caption),
        )

        self._subscription_is_generating = self._is_loading.subscribe(
            lambda status: self._handle_is_loading_update(is_loading=status),
        )

        self._reader.object_urls.subscribe(lambda url: self._handle_object_url_update(url))

    def _handle_description_update(self, description: str) -> None:
        """Handle changes to the description."""
        self._content.innerText = description.capitalize()

    def _handle_is_loading_update(self, *, is_loading: bool) -> None:
        """Handle changes in the loading status."""
        if is_loading:
            self._content.classList.add("skeleton-block")
            self._image_container.classList.add("is-skeleton")
        else:
            self._content.classList.remove("skeleton-block")
            self._image_container.classList.remove("is-skeleton")

    def _handle_object_url_update(self, url: str) -> None:
        """Handle changes to the object URL."""
        self._image.src = url
