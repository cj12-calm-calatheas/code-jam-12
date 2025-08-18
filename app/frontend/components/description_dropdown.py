from typing import TYPE_CHECKING, override
from uuid import uuid4

from js import Event, document
from pyodide.ffi import JsDomElement
from pyodide.ffi.wrappers import add_event_listener

from frontend.base import Component
from frontend.services import pokemon

if TYPE_CHECKING:
    from frontend.components import Description

TEMPLATE = """
<div class="dropdown-content">
    <button id="favourite-{favourite_guid}" class="dropdown-item has-text">
        <span class="icon">
            <i class="fas fa-heart"></i>
        </span>
        <span>Favourite</span>
    </button>
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

    def __init__(self, root: JsDomElement, parent: "Description") -> None:
        super().__init__(root)
        self._parent = parent
        self._favourite_guid = uuid4()
        self._delete_guid = uuid4()

    @override
    def build(self) -> str:
        return TEMPLATE.format(
            favourite_guid=self._favourite_guid,
            delete_guid=self._delete_guid,
        )

    @override
    def on_render(self) -> None:
        if not self._parent._description:
            return

        self._delete_button = document.getElementById(f"delete-{self._delete_guid}")
        self._favourite_button = document.getElementById(f"favourite-{self._favourite_guid}")

        add_event_listener(self._delete_button, "click", self._on_delete_button_click)
        add_event_listener(self._favourite_button, "click", self._on_favourite_button_click)

    def _on_delete_button_click(self, _: Event) -> None:
        if not self._parent._description:
            return

        pokemon.delete(self._parent._description.name)

    def _on_favourite_button_click(self, _: Event) -> None:
        if not self._parent._description:
            return

        pokemon.favourite(self._parent._description.name)
