from typing import override

from js import document
from pyodide.ffi import JsDomElement

from calm_calatheas.base import Component
from calm_calatheas.services import description

TEMPLATE = """
<section class="section">
    <div class="content">
        <p id="caption"></p>
    </div>
</section>
"""


class Description(Component):
    """Test component to demonstrate the descriptions service."""

    def __init__(self, root: JsDomElement) -> None:
        super().__init__(root)
        self._description = description

    @override
    def build(self) -> str:
        return TEMPLATE

    @override
    def on_render(self) -> None:
        self._caption = document.getElementById("caption")
        self._description.descriptions.subscribe(self._handle_description_update)

    def _handle_description_update(self, description: str) -> None:
        """Handle updates to the description."""
        self._caption.textContent = description  # type: ignore[textContent is available]
