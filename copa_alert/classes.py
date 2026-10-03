"""Filtering and change detection for COPA class listings.

Nothing in here touches the network, so it can be tested without logging in.
"""

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

TARGET_DAYS = {"friday", "saturday", "sunday"}
TARGET_MIN_AGE = 12
TARGET_MAX_AGE = 18

_DAY_ALIASES = {
    "fri": "friday",
    "sat": "saturday",
    "sun": "sunday",
    "mon": "monday",
    "tue": "tuesday",
    "tues": "tuesday",
    "wed": "wednesday",
    "thu": "thursday",
    "thur": "thursday",
    "thurs": "thursday",
}


@dataclass(frozen=True)
class ClassListing:
    name: str
    ages: str  # as shown on the site, e.g. "Ages 12-18"
    day: str  # e.g. "Saturday" or "Sat"
    start_time: str  # e.g. "10:00 AM"
    date: str = ""  # specific date, if the site lists one
    instructor: str = ""
    # Deliberately no enrollment or spots-left field: those changes must not
    # make a class look new.

    def key(self) -> str:
        """Stable fingerprint of the class's identity.

        Stored as a hash so the public repo doesn't publish the schedule.
        """
        parts = [self.name, normalize_day(self.day) or self.day, self.start_time, self.date, self.instructor]
        text = "|".join(" ".join(p.lower().split()) for p in parts)
        return hashlib.sha256(text.encode()).hexdigest()


def normalize_day(day: str) -> str | None:
    word = re.sub(r"[^a-z]", "", day.lower())
    if word in _DAY_ALIASES.values():
        return word
    return _DAY_ALIASES.get(word)


def parse_age_range(ages: str) -> tuple[int, int] | None:
    """Turn text like "Ages 12-18", "12 – 18 yrs" or "13+" into (min, max)."""
    m = re.search(r"(\d{1,2})\s*(?:-|–|—|to)\s*(\d{1,2})", ages)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"(\d{1,2})\s*\+", ages)
    if m:
        return int(m.group(1)), 99
    return None


def is_target(listing: ClassListing) -> bool:
    """True for Friday-Sunday classes whose age range lies within 12-18."""
    if normalize_day(listing.day) not in TARGET_DAYS:
        return False
    age_range = parse_age_range(listing.ages)
    if age_range is None:
        return False
    low, high = age_range
    return TARGET_MIN_AGE <= low and high <= TARGET_MAX_AGE


def load_seen(path: Path) -> set[str] | None:
    """Return the stored fingerprints, or None if there is no baseline yet."""
    if not path.exists():
        return None
    return set(json.loads(path.read_text())["seen"])


def save_seen(path: Path, seen: set[str]) -> None:
    path.write_text(json.dumps({"seen": sorted(seen)}, indent=2) + "\n")


def find_new(listings: list[ClassListing], seen: set[str]) -> list[ClassListing]:
    """Target classes whose fingerprint has never been seen before.

    `seen` only ever grows, so a class that drops off the page while full and
    comes back when a spot opens is not reported as new.
    """
    new = []
    keys = set()
    for listing in listings:
        if not is_target(listing):
            continue
        k = listing.key()
        if k not in seen and k not in keys:
            keys.add(k)
            new.append(listing)
    return new
