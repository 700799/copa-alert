"""Logs in to the COPA scheduling page and reads the class listings.

TODO: the login steps and the page structure are not known yet, because the
site could not be reached while this was written. Everything that depends on
them is in `log_in` and `read_listings` below.
"""

import os

from playwright.sync_api import Page, sync_playwright

from .classes import ClassListing

SCHEDULE_URL = os.environ.get("COPA_SCHEDULE_URL", "https://copastc.com/membership-scheduling/")


def log_in(page: Page) -> None:
    """Get past the Clerk sign-in so the schedule is visible.

    Credentials come only from environment variables (GitHub secrets).
    """
    # The access code will be read from os.environ["COPA_ACCESS_CODE"].
    raise NotImplementedError("TODO: fill in the Clerk sign-in steps")


def read_listings(page: Page) -> list[ClassListing]:
    """Read every class on the schedule page (filtering happens elsewhere)."""
    raise NotImplementedError("TODO: map the schedule markup to ClassListing")


def fetch_listings() -> list[ClassListing]:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(SCHEDULE_URL, wait_until="networkidle")
            log_in(page)
            page.goto(SCHEDULE_URL, wait_until="networkidle")
            return read_listings(page)
        finally:
            browser.close()
