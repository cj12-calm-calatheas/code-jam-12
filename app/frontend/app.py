from typing import override

from js import Event, document
from pyodide.ffi.wrappers import add_event_listener

from frontend.base import Component
from frontend.components import Footer, Header, LoadingCaptionModel, Pokemon
from frontend.services import pokemon

TEMPLATE = """
<section id="app-container" class="hero is-fullheight container">
    <div class="hero-head">
        <div id="app-header" class="mb-2"></div>
        <div id="notifications"></div>
    </div>
    <div id="app-body" class="hero-body mx-0">
        <div class="content">
            <h1 class="title is-1">Hello from Python!</h1>
            <h2 class="subtitle">This is a simple app using Pyodide.</h2>
            <section class="section px-0">
                <div class="content">
                    <p>
                        A general description of the app goes here.
                    </p>
                </div>
            </section>
            <div class="level is-mobile">
                <div class="level-left">
                    <h2 class="title is-3 mb-0">Your Pokemon</h2>
                </div>
                <div class="level-right">
                    <div class="level-item">
                        <a id="pokemon-refresh" class="is-size-4">
                            <span class="icon has-text-primary">
                                <i id="pokemon-refresh-icon" class="fas fa-sync-alt"></i>
                            </span>
                        </a>
                    </div>
                </div>
            </div>
            <div id="pokemon"></div>
        </div>
    </div>
    <div id="app-footer" class="hero-foot"></div>
</section>
"""


class App(Component):
    """The main application class."""

    @override
    def build(self) -> str:
        return TEMPLATE

    @override
    def pre_destroy(self) -> None:
        self._footer.destroy()
        self._header.destroy()
        self._loading_caption_model.destroy()

    @override
    def on_render(self) -> None:
        self._footer = Footer(document.getElementById("app-footer"))
        self._footer.render()

        self._header = Header(document.getElementById("app-header"))
        self._header.render()

        self._notifications = document.getElementById("notifications")
        self._loading_caption_model = LoadingCaptionModel(self._notifications)

        self._pokemon = Pokemon(document.getElementById("pokemon"))
        self._pokemon.render()

        self._pokemon_refresh = document.getElementById("pokemon-refresh")
        self._pokemon_refresh_icon = document.getElementById("pokemon-refresh-icon")
        add_event_listener(self._pokemon_refresh, "click", self._on_pokemon_refresh)

        pokemon.is_refreshing.subscribe(
            lambda is_refreshing: self._handle_pokemon_is_refreshing(
                is_refreshing=is_refreshing,
            ),
        )

    def _on_pokemon_refresh(self, event: Event) -> None:
        """Handle the Pokemon refresh button click event."""
        if event.currentTarget.hasAttribute("disabled"):  # type: ignore[currentTarget is available]
            return

        pokemon.refresh()

    def _handle_pokemon_is_refreshing(self, *, is_refreshing: bool) -> None:
        """Handle the Pokemon refresh state."""
        if is_refreshing:
            self._pokemon_refresh.setAttribute("disabled", "")
            self._pokemon_refresh_icon.classList.add("fa-spin")
        else:
            self._pokemon_refresh.removeAttribute("disabled")
            self._pokemon_refresh_icon.classList.remove("fa-spin")
