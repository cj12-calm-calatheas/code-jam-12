from typing import override

import reactivex.operators as op
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

        # Update the UI whenever the loading state changes
        caption.is_loading_model.pipe(
            op.distinct_until_changed(),
            op.take_until(self.destroyed),
        ).subscribe(
            lambda is_loading: self._handle_is_loading_update(is_loading=is_loading),
        )

    @override
    def build(self) -> str:
        return TEMPLATE

    def _handle_is_loading_update(self, *, is_loading: bool) -> None:
        """Show the notification while the model is loading."""
        if is_loading:
            self.render()
        else:
            self.remove()
