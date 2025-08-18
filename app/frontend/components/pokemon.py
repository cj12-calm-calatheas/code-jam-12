from typing import override

import reactivex.operators as op
from js import document
from pyodide.ffi import JsDomElement
from reactivex import combine_latest

from frontend.base import Component
from frontend.components import Description
from frontend.models import PokemonRecord
from frontend.services import pokemon

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

        # Update the UI whenever the list of pokemon or the loading state changes
        combine_latest(pokemon.pokemon, pokemon.is_generating).pipe(
            op.take_until(self.destroyed),
        ).subscribe(lambda params: self._render_pokemon(params[0], is_generating=params[1]))

    def _render_pokemon(self, pokemon: list[PokemonRecord], *, is_generating: bool) -> None:
        """Render the given list of Pokemon."""
        for component in self._current_pokemon:
            component.destroy()

        while cell := self._pokemon_grid.firstChild:
            self._pokemon_grid.removeChild(cell)

        self._current_pokemon = []

        if not (pokemon or is_generating):
            self._pokemon_grid.innerHTML = EMPTY_PLACEHOLDER_TEMPLATE  # type: ignore[innerHTML is available]
            return

        for item in pokemon:
            cell = document.createElement("div")
            cell.classList.add("cell")

            description = Description(cell, item)

            self._pokemon_grid.appendChild(cell)
            self._current_pokemon.append(description)

            description.render()

        if is_generating:
            self._render_generating_placeholder()

    def _render_generating_placeholder(self) -> None:
        """Render a placeholder in the Pokemon grid while generating."""
        if placeholder := document.getElementById("pokemon-empty-placeholder"):
            placeholder.remove()  # type: ignore[remove is available]

        cell = document.createElement("div")
        cell.classList.add("cell")

        # Create a description component with no data to show loading state
        description = Description(cell, None)
        description.render()

        self._pokemon_grid.prepend(cell)  # type: ignore[prepend is available]
        self._current_pokemon.append(description)
