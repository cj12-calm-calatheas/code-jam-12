from typing import TYPE_CHECKING, cast, override

import reactivex.operators as op
from js import document
from pyodide.ffi import JsDomElement
from reactivex import combine_latest

from frontend.base import Component
from frontend.services import PokemonDescription, caption, description, reader

if TYPE_CHECKING:
    from js import JsImgElement


TYPE_TEMPLATE = """
<span class="tag {type_class}">{type_name}</span>
"""

TEMPLATE = """
<div id="description-container" class="box">
    <article class="media">
        <figure class="media-left">
            <p id="description-image-container" class="image is-128x128">
                <img id="description-image" />
            </p>
        </figure>
        <div class="media-content">
            <div id="description-content">
                <div id="description-header" class="mb-4">
                    <div id="description-name" class="title is-4"></div>
                    <div id="description-category" class="subtitle is-6"></div>
                    <div id="description-types" class="tags has-addons"></div>
                </div>
                <p id="description-flavor-text" class="content"></p>
                <div class="field is-grouped is-grouped-multiline has-text-7">
                    <div class="control">
                        <div class="tags has-addons">
                            <span class="tag">Ability</span>
                            <span class="tag is-info" id="description-ability"></span>
                        </div>
                    </div>
                    <div class="control">
                        <div class="tags has-addons">
                            <span class="tag">Habitat</span>
                            <span class="tag is-info" id="description-habitat"></span>
                        </div>
                    </div>
                    <div class="control">
                        <div class="tags has-addons">
                            <span class="tag">Height</span>
                            <span class="tag is-info" id="description-height"></span>
                        </div>
                    </div>
                    <div class="control">
                        <div class="tags has-addons">
                            <span class="tag">Weight</span>
                            <span class="tag is-info" id="description-weight"></span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </article>
</div>
"""


class Description(Component):
    """Test component to demonstrate the descriptions service."""

    def __init__(self, root: JsDomElement) -> None:
        super().__init__(root)
        self._caption = caption
        self._description = description
        self._reader = reader

        self._is_loading = combine_latest(
            self._caption.is_generating_caption,
            self._description.is_generating_description,
            self._reader.is_reading,
        ).pipe(op.map(lambda is_loading: any(is_loading)))

        self._subscription_handle_render = self._is_loading.subscribe(
            lambda is_loading: self._handle_render(is_loading=is_loading),
        )

    @override
    def build(self) -> str:
        return TEMPLATE

    @override
    def on_destroy(self) -> None:
        self._subscription_handle_render.dispose()
        self._subscription_update_descriptions.dispose()
        self._subscription_handle_display_loader.dispose()

    @override
    def on_render(self) -> None:
        self._description_header = document.getElementById("description-header")
        self._content = document.getElementById("description-content")

        self._image = cast("JsImgElement", document.getElementById("description-image"))
        self._image_container = document.getElementById("description-image-container")

        self._name = document.getElementById("description-name")
        self._category = document.getElementById("description-category")
        self._types = document.getElementById("description-types")

        self._flavor_text = document.getElementById("description-flavor-text")

        self._ability = document.getElementById("description-ability")
        self._habitat = document.getElementById("description-habitat")
        self._height = document.getElementById("description-height")
        self._weight = document.getElementById("description-weight")

        self._subscription_update_descriptions = self._description.descriptions.subscribe(
            lambda description: self._handle_update_descriptions(description),
        )

        self._subscription_handle_display_loader = self._is_loading.subscribe(
            lambda is_loading: self._handle_display_loader(is_loading=is_loading),
        )

        self._reader.object_urls.subscribe(lambda url: self._handle_object_url_update(url))

    def _handle_update_descriptions(self, description: PokemonDescription) -> None:
        """Handle changes to the description."""
        self._name.innerText = description.name
        self._category.innerText = f"The {description.category.capitalize()} Pokemon"
        self._flavor_text.innerText = description.flavor_text
        self._ability.innerText = description.ability.capitalize()
        self._habitat.innerText = description.habitat.capitalize()
        self._height.innerText = f"{description.height} m"
        self._weight.innerText = f"{description.weight} kg"

        types = "\n".join(
            TYPE_TEMPLATE.format(type_name=type_.capitalize(), type_class=f"type-{type_}")
            for type_ in description.types
        )

        self._types.innerHTML = types  # type: ignore[innerHTML attribute is available]

    def _handle_render(self, *, is_loading: bool) -> None:
        """Handle the rendering of the component."""
        if is_loading and not self.element:
            self.render()

    def _handle_display_loader(self, *, is_loading: bool) -> None:
        """Handle changes in the loading status."""
        if is_loading:
            self._image_container.classList.add("is-skeleton")
            self._description_header.classList.add("skeleton-block")
            self._flavor_text.classList.add("skeleton-block")
            self._ability.classList.add("is-skeleton")
            self._habitat.classList.add("is-skeleton")
            self._height.classList.add("is-skeleton")
            self._weight.classList.add("is-skeleton")

            # Set empty content to ensure loaders take up roughly the expected space
            self._name.innerHTML = "&nbsp;"  # type: ignore[innerHTML attribute is available]
            self._category.innerHTML = "&nbsp;"  # type: ignore[innerHTML attribute is available]
            self._types.innerHTML = "&nbsp;"  # type: ignore[innerHTML attribute is available]
        else:
            self._image_container.classList.remove("is-skeleton")
            self._description_header.classList.remove("skeleton-block")
            self._flavor_text.classList.remove("skeleton-block")
            self._ability.classList.remove("is-skeleton")
            self._habitat.classList.remove("is-skeleton")
            self._height.classList.remove("is-skeleton")
            self._weight.classList.remove("is-skeleton")

    def _handle_object_url_update(self, url: str) -> None:
        """Handle changes to the object URL."""
        self._image.src = url
