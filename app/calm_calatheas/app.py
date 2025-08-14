from typing import override

from js import document

from calm_calatheas.base import Component
from calm_calatheas.components import Description, Footer, Header

TEMPLATE = """
<section class="hero is-fullheight container">
    <div id="app-header" class="hero-head"></div>
    <div id="app-body" class="hero-body">
        <div class="content">
            <h1 class="title is-1">Hello from Python!</h1>
            <h2 class="subtitle">This is a simple app using Pyodide.</h2>
            <section class="section px-0">
                <div class="content">
                    <p>
                        A general description of the app goes here.
                    </p>
                </div>
                <button class="button is-large is-primary">Get started!</button>
            </section>
            <div id="description-test"></div>
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
        self._description.destroy()

    @override
    def on_render(self) -> None:
        self._footer = Footer(document.getElementById("app-footer"))
        self._footer.render()

        self._header = Header(document.getElementById("app-header"))
        self._header.render()

        self._description = Description(document.getElementById("description-test"))
        self._description.render()
