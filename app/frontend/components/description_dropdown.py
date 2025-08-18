from typing import override
from uuid import uuid4

from js import Event, document
from pyodide.ffi import JsDomElement
from pyodide.ffi.wrappers import add_event_listener

from frontend.base import Component
from frontend.models import PokemonRecord
from frontend.services import pokemon

TEMPLATE = """
<div class="dropdown-content">
    <button id="favourite-{favourite_guid}" class="dropdown-item has-text">
        <span class="icon">
            <i class="fas fa-heart"></i>
        </span>
        <span>{favourite_text}</span>
    </button>
    <hr class="dropdown-divider" />
    <button id="delete-{delete_guid}" class="dropdown-item has-text-danger">
        <span class="icon">
            <i class="fas fa-trash"></i>
        </span>
        <span>Delete</span>
    </button>
</div>
"""


class DescriptionDropdown(Component):
    """Dropdown for Pokemon descriptions."""

    def __init__(self, root: JsDomElement, description: PokemonRecord) -> None:
        super().__init__(root)
        self._description = description
        self._favourite_guid = uuid4()
        self._delete_guid = uuid4()

    @override
    def build(self) -> str:
        return TEMPLATE.format(
            favourite_guid=self._favourite_guid,
            favourite_text="Unfavourite" if self._description.favourite else "Favourite",
            delete_guid=self._delete_guid,
        )

    @override
    def on_render(self) -> None:
        self._delete_button = document.getElementById(f"delete-{self._delete_guid}")
        self._favourite_button = document.getElementById(f"favourite-{self._favourite_guid}")

        add_event_listener(self._delete_button, "click", self._on_delete_button_click)
        add_event_listener(self._favourite_button, "click", self._on_favourite_button_click)

    def _on_delete_button_click(self, _: Event) -> None:
        pokemon.delete(self._description.name)

    def _on_favourite_button_click(self, _: Event) -> None:
        self._description.favourite = not self._description.favourite
        pokemon.put(self._description)
