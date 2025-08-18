from collections.abc import Generator
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect
from testcontainers.compose import DockerCompose

DESCRIPTION_GENERATED_TIMEOUT_MS = 600000
CAPTION_MODEL_LOADED_TIMEOUT_MS = 30000
PYSCRIPT_READY_TIMEOUT_MS = 30000


@pytest.fixture(scope="session")
def compose() -> Generator[DockerCompose]:
    """Return a Docker Compose instance."""
    with DockerCompose(context=Path(__file__).parent.absolute(), build=True) as compose:
        yield compose


@pytest.fixture(scope="session")
def base_url(compose: DockerCompose) -> str:
    """Return the base URL for the application."""
    port = compose.get_service_port("app", 8000)
    return f"http://localhost:{port}"


@pytest.fixture()
def app(base_url: str, page: Page) -> Page:
    """Navigate to the home page, wait for PyScript load and return the page instance."""
    page.goto(base_url)

    page.wait_for_event(
        event="console",
        predicate=lambda event: "PyScript Ready" in event.text,
        timeout=PYSCRIPT_READY_TIMEOUT_MS,
    )

    return page


@pytest.fixture()
def model_loaded(app: Page) -> Page:
    """Wait for the caption model to be loaded."""
    notification = app.get_by_text("Loading the model for generating captions")

    expect(notification).to_be_visible()
    expect(notification).not_to_be_visible(timeout=CAPTION_MODEL_LOADED_TIMEOUT_MS)

    return app
