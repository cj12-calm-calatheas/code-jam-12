import re

from playwright.sync_api import Page, expect


def test__main_page_has_welcome_message(app: Page) -> None:
    """
    Test that the main page has a welcome message.

    Asserts:
        - The welcome message is visible on the page.
    """
    expect(app.get_by_text(re.compile("Hello from Python!"))).to_be_visible()
