"""Opens the public COPA schedule and reads the sessions it loads.

The schedule on copastc.com/membership-scheduling/ is an embedded Retool app.
When it opens, it downloads every session for about the next two weeks in one
request and then filters on screen, so the page is loaded once, normally, and
that download is read. No login is needed.
"""

import json
import os

from playwright.sync_api import sync_playwright

from .classes import Session, parse_schedule

SCHEDULE_URL = "https://copa.retool.com/embedded/public/55172728-5a4a-43b1-baab-b4fc863de60c"
SCHEDULE_QUERY = "queryName=Daysmart_Schedule_Data"


def fetch_sessions() -> list[Session]:
    with sync_playwright() as p:
        # CHROMIUM_PATH is only for running locally against a preinstalled browser.
        browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        try:
            page = browser.new_page()
            with page.expect_response(lambda r: SCHEDULE_QUERY in r.url, timeout=90_000) as info:
                page.goto(SCHEDULE_URL)
            response = info.value
            if not response.ok:
                raise RuntimeError(f"Schedule request failed with HTTP {response.status}")
            return parse_schedule(json.loads(response.text()))
        finally:
            browser.close()
