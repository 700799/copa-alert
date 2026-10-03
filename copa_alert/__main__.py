"""Entry point: python -m copa_alert

Logs only counts, never class details, because Actions logs on a public repo
are visible to anyone.
"""

import sys
from pathlib import Path

from .classes import find_new, is_target, load_seen, save_seen
from .notify import format_email, send_email
from .scraper import fetch_listings

STATE_FILE = Path("seen.json")


def main() -> int:
    listings = fetch_listings()
    targets = [c for c in listings if is_target(c)]
    print(f"Read {len(listings)} classes, {len(targets)} are 12-18 on Fri-Sun.")

    if not listings:
        # Most likely a failed login or a changed page. Fail so GitHub emails
        # about the broken run, and leave the stored state alone.
        print("No classes found; not updating state.", file=sys.stderr)
        return 1

    seen = load_seen(STATE_FILE)
    if seen is None:
        save_seen(STATE_FILE, {c.key() for c in targets})
        print("First run: saved baseline, no email sent.")
        return 0

    new = find_new(listings, seen)
    print(f"{len(new)} new.")
    if new:
        send_email(format_email(new))
        save_seen(STATE_FILE, seen | {c.key() for c in new})
    return 0


if __name__ == "__main__":
    sys.exit(main())
