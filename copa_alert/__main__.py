"""Entry point: python -m copa_alert [--dry-run]

--dry-run prints what would be emailed and doesn't send or save anything.
"""

import sys
from pathlib import Path

from .classes import is_target, load_state, save_state, update
from .notify import format_email, send_email
from .scraper import fetch_sessions

STATE_FILE = Path("seen.json")


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    sessions = fetch_sessions()
    targets = [s for s in sessions if is_target(s)]
    print(f"Read {len(sessions)} sessions, {len(targets)} are 12-19 on Fri-Sun.")

    if not sessions:
        # Most likely the page changed. Fail so GitHub emails about the broken
        # run, and leave the stored state alone.
        print("No sessions found; not updating state.", file=sys.stderr)
        return 1

    state = load_state(STATE_FILE)
    added, new_state = update(state, sessions)
    if state is None:
        print("First run: saved baseline, no email sent.")
    else:
        print(f"{len(added)} newly added.")

    if dry_run:
        if added:
            print(format_email(added))
        return 0
    if added:
        send_email(format_email(added))
    save_state(STATE_FILE, new_state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
