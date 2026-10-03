"""Filtering and change detection for COPA sessions.

Nothing in here touches the network, so it can be tested without a browser.

The schedule only shows roughly the next two weeks, so new dates roll into
view every day. A session counts as added only when it shows up on a date
that an earlier check could already see; sessions on dates that just came
into view are recorded without an alert.
"""

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

TARGET_PROGRAM = "12 - 19yrs"
TARGET_WEEKDAYS = {4, 5, 6}  # Friday, Saturday, Sunday


@dataclass(frozen=True)
class Session:
    event_id: str
    program: str  # age group, e.g. "12 - 19yrs"
    name: str  # e.g. "SC: SoccerBot 360 (LV1)"
    date: str  # YYYY-MM-DD
    start: str  # local wall time, HH:MM
    end: str

    @classmethod
    def from_row(cls, row: dict) -> "Session":
        # The site labels local times with "Z"; the UI shows them unconverted.
        return cls(
            event_id=row["s_eventid"],
            program=(row["programname"] or "").strip(),
            name=(row["teamname"] or row["leaguedesc"] or "").strip(),
            date=row["start_date"],
            start=row["s_eventstart"][11:16],
            end=row["s_eventend"][11:16],
        )


def parse_schedule(payload: list) -> list[Session]:
    """Turn the schedule query's column-oriented result into sessions."""
    cols = payload[0]["cols"]
    data = payload[0]["data"][0]
    return [Session.from_row(dict(zip(cols, values))) for values in zip(*data)]


def is_target(s: Session) -> bool:
    return s.program == TARGET_PROGRAM and date.fromisoformat(s.date).weekday() in TARGET_WEEKDAYS


@dataclass
class State:
    seen: dict[str, str]  # event id -> date
    seen_through: str  # latest date visible in a previous check


def load_state(path: Path) -> State | None:
    """Return the stored state, or None if there is no baseline yet."""
    if not path.exists():
        return None
    raw = json.loads(path.read_text())
    return State(seen=raw["seen"], seen_through=raw["seen_through"])


def save_state(path: Path, state: State) -> None:
    path.write_text(json.dumps({"seen_through": state.seen_through, "seen": dict(sorted(state.seen.items()))}, indent=1) + "\n")


def update(state: State | None, sessions: list[Session]) -> tuple[list[Session], State]:
    """Return (newly added target sessions, new state)."""
    targets = [s for s in sessions if is_target(s)]
    latest = max((s.date for s in sessions), default="")
    if state is None:
        return [], State({s.event_id: s.date for s in targets}, latest)

    added = []
    for s in targets:
        if s.event_id not in state.seen and s.date <= state.seen_through:
            added.append(s)
    added.sort(key=lambda s: (s.date, s.start, s.name))

    # Forget dates that have left the site's window. Using the feed's own
    # earliest date avoids time zone mistakes about what "today" is.
    earliest = min((s.date for s in sessions), default="")
    seen = {k: v for k, v in state.seen.items() if v >= earliest}
    seen.update({s.event_id: s.date for s in targets})
    return added, State(seen, max(state.seen_through, latest))
