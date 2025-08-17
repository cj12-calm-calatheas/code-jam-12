from typing import override

import reactivex.operators as ops
from pyodide.ffi import JsDomElement

from frontend.base import Component
from frontend.services import caption

TEMPLATE = """
<div class="notification is-info">
    <p>Loading the model for generating captions</p>
    <progress class="progress is-small mt-4" max="100"></progress>
</div>
"""


class LoadingCaptionModel(Component):
    """A component that shows a loading indicator while the caption model is being loaded."""

    def __init__(self, root: JsDomElement) -> None:
        super().__init__(root)
        self._subscription_is_loading = caption.is_loading_model.pipe(ops.distinct_until_changed()).subscribe(
            lambda is_loading: self._handle_is_loading_update(is_loading=is_loading),
        )

    @override
    def build(self) -> str:
        return TEMPLATE

    @override
    def on_destroy(self) -> None:
        self._subscription_is_loading.dispose()

    def _handle_is_loading_update(self, *, is_loading: bool) -> None:
        """Handle updates to the loading state."""
        if is_loading:
            self.render()
        else:
            self.remove()
