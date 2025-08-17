from abc import ABC, abstractmethod
from typing import cast
from uuid import uuid4

from js import DOMParser
from pyodide.ffi import JsDomElement


class Component(ABC):
    """A base class for all components."""

    parser = DOMParser.new()  # type: ignore[]

    def __init__(self, root: JsDomElement) -> None:
        self.element: JsDomElement | None = None
        self.guid = uuid4()
        self.root = root

    @abstractmethod
    def build(self) -> str:
        """Build the component's template and output it as an HTML string."""

    def destroy(self) -> None:
        """Destroy the component and clean up resources."""
        self.remove()
        self.on_destroy()

    def on_destroy(self) -> None:
        """Hook to perform actions after the component is destroyed."""
        return

    def on_render(self) -> None:
        """Hook to perform actions after rendering the component."""
        return

    def pre_destroy(self) -> None:
        """Hook to perform actions before the component is destroyed."""
        return

    def pre_render(self) -> None:
        """Hook to perform actions before rendering the component."""
        return

    def remove(self) -> None:
        """Remove the component's element from the DOM."""
        if self.element:
            self.element.remove()  # type: ignore[remove method is available]

    def render(self) -> None:
        """Create a new DOM element for the component and append it to the root element."""
        self.pre_render()

        # Render the given template as an HTML document
        template = self.build()
        document = self.parser.parseFromString(template, "text/html")

        # Take the first child of the body and append it to the root element
        self.element = cast("JsDomElement", document.body.firstChild)
        self.root.appendChild(self.element)

        self.on_render()
