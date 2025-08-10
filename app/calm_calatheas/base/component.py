from abc import ABC, abstractmethod

from js import document
from pyodide.ffi import JsDomElement


class Component(ABC):
    """A base class for all components."""

    def __init__(
        self,
        root: JsDomElement,
        *,
        classes: list[str] | None = None,
        element_type: str = "div",
    ) -> None:
        self.root = root

        self.classes = classes
        self.element_type = element_type

        self.on_init()

    @abstractmethod
    def build(self) -> str:
        """Build the component's template and output it as an HTML string."""

    def destroy(self) -> None:
        """Destroy the component and clean up resources."""
        self.element.remove()  # type: ignore[remove attribute is available but not typed]
        self.on_destroy()

    def on_destroy(self) -> None:
        """Hook to perform actions after the component is destroyed."""
        return

    def on_init(self) -> None:
        """Hook to perform actions after initializing the component."""
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

    def render(self) -> None:
        """Create a new DOM element for the component and append it to the root element."""
        self.pre_render()

        self.element = document.createElement(self.element_type)
        self.element.innerHTML = self.build()  # type: ignore[innerHTML attribute is available but not typed]

        for class_name in self.classes or []:
            self.element.classList.add(class_name)

        self.root.appendChild(self.element)
        self.on_render()
