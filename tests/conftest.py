from collections.abc import Generator
from pathlib import Path

import pytest
from playwright.sync_api import Page
from testcontainers.compose import DockerCompose

PYSCRIPT_READY_TIMEOUT_MS = 20000


@pytest.fixture(scope="session")
def compose() -> Generator[DockerCompose]:
    """Return a Docker Compose instance."""
    with DockerCompose(context=Path(__file__).parent.absolute(), build=True) as compose:
        yield compose


@pytest.fixture(scope="session")
def base_url(compose: DockerCompose) -> str:
    """Return the base URL for the application."""
    port = compose.get_service_port("app", 80)
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
