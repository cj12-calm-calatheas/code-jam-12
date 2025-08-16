import re

from conftest import PYSCRIPT_READY_TIMEOUT_MS
from playwright.sync_api import Page, expect


def test__main_page_has_welcome_message(app: Page) -> None:
    """
    Test that the main page has a welcome message.

    Asserts:
        - The welcome message is visible on the page.
    """
    expect(app.get_by_text(re.compile("Hello from Python!"))).to_be_visible()


def test__default_theme_is_system_preferred(app: Page) -> None:
    """
    Test that the default theme is the system preferred theme.

    Asserts:
        - The system preferred theme is applied by default.
    """
    expect(app.locator("html")).not_to_have_attribute("data-theme", re.compile("dark|light"))


def test__switch_to_dark_theme(app: Page) -> None:
    """
    Test that switching to the dark theme works.

    Asserts:
        - The dark theme is applied when the user selects it.
    """
    theme_selector = app.locator(".navbar-item", has_text="Theme")
    expect(theme_selector).to_be_visible()
    theme_selector.hover()

    dark_mode_selector = theme_selector.locator(".navbar-item", has_text="Dark")
    expect(dark_mode_selector).to_be_visible()
    dark_mode_selector.click()

    expect(app.locator("html")).to_have_attribute("data-theme", "dark")


def test__switch_to_light_theme(app: Page) -> None:
    """
    Test that switching to the light theme works.

    Asserts:
        - The light theme is applied when the user selects it.
    """
    theme_selector = app.locator(".navbar-item", has_text="Theme")
    expect(theme_selector).to_be_visible()
    theme_selector.hover()

    light_mode_selector = theme_selector.locator(".navbar-item", has_text="Light")
    expect(light_mode_selector).to_be_visible()
    light_mode_selector.click()

    expect(app.locator("html")).to_have_attribute("data-theme", "light")


def test__switch_to_system_theme(app: Page) -> None:
    """
    Test that switching to the system theme works.

    Asserts:
        - The system theme is applied when the user selects it.
    """
    theme_selector = app.locator(".navbar-item", has_text="Theme")
    expect(theme_selector).to_be_visible()
    theme_selector.hover()

    # First switch to light theme to ensure a theme is applied
    dark_mode_selector = theme_selector.locator(".navbar-item", has_text="Dark")
    expect(dark_mode_selector).to_be_visible()
    dark_mode_selector.click()

    expect(app.locator("html")).to_have_attribute("data-theme", "dark")

    # Next switch (back) to the system theme
    auto_mode_selector = theme_selector.locator(".navbar-item", has_text="Auto")
    expect(auto_mode_selector).to_be_visible()
    auto_mode_selector.click()

    expect(app.locator("html")).not_to_have_attribute("data-theme", re.compile("dark|light"))


def test__theme_is_restored_after_refresh(app: Page) -> None:
    """
    Test that the selected theme is restored after a page refresh.

    Asserts:
        - The theme remains consistent after refreshing the page.
    """
    # Switch to dark theme
    theme_selector = app.locator(".navbar-item", has_text="Theme")
    expect(theme_selector).to_be_visible()
    theme_selector.hover()

    dark_mode_selector = theme_selector.locator(".navbar-item", has_text="Dark")
    expect(dark_mode_selector).to_be_visible()
    dark_mode_selector.click()

    expect(app.locator("html")).to_have_attribute("data-theme", "dark")

    # Refresh the page
    app.reload()

    app.wait_for_event(
        event="console",
        predicate=lambda event: "PyScript Ready" in event.text,
        timeout=PYSCRIPT_READY_TIMEOUT_MS,
    )

    # Check that the dark theme is still applied
    expect(app.locator("html")).to_have_attribute("data-theme", "dark")
