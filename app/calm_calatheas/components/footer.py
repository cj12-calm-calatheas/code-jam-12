from typing import override

from calm_calatheas.base import Component

TEMPLATE = """
<nav class="tabs is-boxed is-fullwidth">
    <ul>
        <li id="camera-button">
            <button class="button is-large is-fullwidth is-text">
                <span class="icon is-large has-text-primary">
                    <i class="fa-regular fa-camera"></i>
                </span>
            </button>
        </li>
    </ul>
</nav>
"""


class Footer(Component):
    """Footer for the application."""

    @override
    def build(self) -> str:
        return TEMPLATE
