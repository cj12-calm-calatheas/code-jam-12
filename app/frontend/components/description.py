from typing import override

from js import Event, document
from pyodide.ffi import JsDomElement
from pyodide.ffi.wrappers import add_event_listener

from frontend.base import Component
from frontend.models import PokemonRecord
from frontend.services import pokemon

TYPE_TEMPLATE = """
<span class="tag type-{type_class}">{type_name}</span>
"""

LOADING_TEMPLATE = """
<div class="box is-flex is-flex-direction-column" style="height: 100%">
    <article class="media">
        <figure class="media-left">
            <p class="image is-128x128 is-skeleton"></p>
        </figure>
        <div class="media-content">
            <div>
                <p class="title is-4 is-skeleton">Name</p>
                <p class="subtitle is-6 is-skeleton">Category</p>
                <div class="tags has-addons">
                    <span class="tag is-skeleton">Type</span>
                </div>
            </div>
        </div>
        <div class="media-right">
            <button class="is-skeleton">
                <span class="icon">
                    <i class="fa-solid fa-ellipsis"></i>
                </span>
            </button>
        </div>
    </article>
    <div class="is-flex-grow-1 skeleton-block"></div>
    <div class="field is-grouped is-grouped-multiline has-text-7">
        <div class="control">
            <div class="tags has-addons">
                <span class="tag is-skeleton">Ability</span>
            </div>
        </div>
        <div class="control">
            <div class="tags has-addons">
                <span class="tag is-skeleton">Habitat</span>
            </div>
        </div>
        <div class="control">
            <div class="tags has-addons">
                <span class="tag is-skeleton">Height</span>
            </div>
        </div>
        <div class="control">
            <div class="tags has-addons">
                <span class="tag is-skeleton">Weight</span>
            </div>
        </div>
    </div>
</div>
"""


TEMPLATE = """
<div class="box is-flex is-flex-direction-column" style="height: 100%;">
    <article class="media">
        <figure class="media-left">
            <p class="image is-128x128" style="overflow: hidden">
                <img src="{image_url}" alt="{name}" />
            </p>
        </figure>
        <div class="media-content">
            <div>
                <p class="title is-4">{name}</p>
                <p class="subtitle is-6">The {category} Pokemon</p>
                <div class="tags has-addons">{types}</div>
            </div>
        </div>
        <div class="media-right">
            <div class="dropdown is-right is-hoverable">
                <div class="dropdown-trigger">
                    <button aria-label="Context" aria-haspopup="true" aria-controls="dropdown-{guid}">
                        <span class="icon">
                            <i class="fa-solid fa-ellipsis"></i>
                        </span>
                    </button>
                </div>
                <div class="dropdown-menu" id="dropdown-{guid}" role="menu">
                    <div class="dropdown-content">
                        <button id="delete-{guid}" class="dropdown-item has-text-danger">
                            <span class="icon">
                                <i class="fas fa-trash"></i>
                            </span>
                            <span>Delete</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </article>
    <div class="is-flex-grow-1 content">
        <p>{flavor_text}</p>
    </div>
    <div class="field is-grouped is-grouped-multiline has-text-7">
        <div class="control">
            <div class="tags has-addons">
                <span class="tag">Ability</span>
                <span class="tag is-info">{ability}</span>
            </div>
        </div>
        <div class="control">
            <div class="tags has-addons">
                <span class="tag">Habitat</span>
                <span class="tag is-info">{habitat}</span>
            </div>
        </div>
        <div class="control">
            <div class="tags has-addons">
                <span class="tag">Height</span>
                <span class="tag is-info">{height} m</span>
            </div>
        </div>
        <div class="control">
            <div class="tags has-addons">
                <span class="tag">Weight</span>
                <span class="tag is-info">{weight} kg</span>
            </div>
        </div>
    </div>
</div>
"""


class Description(Component):
    """Test component to demonstrate the descriptions service."""

    def __init__(self, root: JsDomElement, description: PokemonRecord | None) -> None:
        super().__init__(root)
        self._description = description

    @override
    def build(self) -> str:
        if not self._description:
            return LOADING_TEMPLATE

        types = "\n".join(
            TYPE_TEMPLATE.format(type_class=type_, type_name=type_.capitalize()) for type_ in self._description.types
        )

        return TEMPLATE.format(
            guid=self.guid,
            image_url=self._description.img_url,
            name=self._description.name,
            category=self._description.category.capitalize(),
            types=types,
            flavor_text=self._description.flavor_text,
            ability=self._description.ability.capitalize(),
            habitat=self._description.habitat.capitalize(),
            height=self._description.height,
            weight=self._description.weight,
        )

    @override
    def on_render(self) -> None:
        if not self._description:
            return

        self._delete_button = document.getElementById(f"delete-{self.guid}")

        add_event_listener(self._delete_button, "click", self._on_delete_button_click)

    def _on_delete_button_click(self, _: Event) -> None:
        if not self._description:
            return

        pokemon.delete(self._description.name)
