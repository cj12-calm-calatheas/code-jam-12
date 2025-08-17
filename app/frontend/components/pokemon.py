from typing import override

import reactivex.operators as ops
from js import document
from pyodide.ffi import JsDomElement
from reactivex import combine_latest

from frontend.base import Component
from frontend.components import Description
from frontend.models import PokemonRecord
from frontend.services import caption, description, pokemon, reader

EMPTY_PLACEHOLDER_TEMPLATE = """
<p id="pokemon-empty-placeholder">Nothing to show here yet!</p>
"""

TEMPLATE = """
<div id="pokemon-grid" class="grid is-col-min-20">
    <p>Nothing to show here yet!</p>
</div>
"""


class Pokemon(Component):
    """The list of Pokemon."""

    def __init__(self, root: JsDomElement) -> None:
        super().__init__(root)
        self._current_pokemon = []

    @override
    def build(self) -> str:
        return TEMPLATE

    @override
    def on_render(self) -> None:
        self._pokemon_grid = document.getElementById("pokemon-grid")

        # Show a loading placeholder whenever the app is busy generating a new Pokemon
        combine_latest(
            caption.is_generating_caption,
            description.is_generating_description,
            reader.is_reading,
        ).pipe(
            ops.map(lambda is_loading: any(is_loading)),
            ops.distinct_until_changed(),
            ops.filter(lambda is_loading: is_loading),
        ).subscribe(lambda _: self._render_loading_placeholder())

        # Sort the Pokemon by timestamp (newest first)
        pokemon.pokemon.pipe(
            ops.map(
                lambda pokemon: sorted(
                    pokemon,
                    key=lambda p: p.timestamp,
                    reverse=True,
                ),
            ),
        ).subscribe(self._render_pokemon)

    def _render_pokemon(self, pokemon: list[PokemonRecord]) -> None:
        """Render the given list of Pokemon."""
        for component in self._current_pokemon:
            component.destroy()

        while cell := self._pokemon_grid.firstChild:
            self._pokemon_grid.removeChild(cell)

        self._current_pokemon = []

        if not pokemon:
            self._pokemon_grid.innerHTML = EMPTY_PLACEHOLDER_TEMPLATE  # type: ignore[innerHTML is available]
            return

        for item in pokemon:
            cell = document.createElement("div")
            cell.classList.add("cell")

            description = Description(cell, item)

            self._pokemon_grid.appendChild(cell)
            self._current_pokemon.append(description)

            description.render()

    def _render_loading_placeholder(self) -> None:
        """Render a loading placeholder in the Pokemon grid."""
        if placeholder := document.getElementById("pokemon-empty-placeholder"):
            placeholder.remove()  # type: ignore[remove is available]

        cell = document.createElement("div")
        cell.classList.add("cell")

        # Create a description component with no data to show loading state
        description = Description(cell, None)
        description.render()

        self._pokemon_grid.prepend(cell)  # type: ignore[prepend is available]
        self._current_pokemon.append(description)
