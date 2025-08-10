from typing import override

from pyodide.ffi import JsDomElement

from calm_calatheas.base import Component

TEMPLATE = """
<ul>
    <li id="camera-button">
        <button class="button is-large is-fullwidth is-text">
            <span class="icon is-large has-text-primary">
                <i class="fa-regular fa-camera"></i>
            </span>
        </button>
    </li>
</ul>
"""


class Footer(Component):
    """Footer for the application."""

    def __init__(self, root: JsDomElement) -> None:
        super().__init__(
            root=root,
            classes=["tabs", "is-boxed", "is-fullwidth"],
            element_type="nav",
        )

    @override
    def build(self) -> str:
        return TEMPLATE
