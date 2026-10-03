"""Filtering and change detection for COPA sessions.

Nothing in here touches the network, so it can be tested without a browser.

The schedule only shows roughly the next two weeks, so new dates roll into
view every day. A session counts as added only when it shows up on a date
that an earlier check could already see; sessions on dates that just came
into view are recorded without an alert.
"""

import json
from dataclasses import asdict, dataclass, field
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
    spots_left: str = field(default="", compare=False)  # not part of identity

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
            spots_left="" if row.get("spots_left") is None else str(row["spots_left"]),
        )


def parse_schedule(payload: list) -> list[Session]:
    """Turn the schedule query's column-oriented result into sessions."""
    cols = payload[0]["cols"]
    data = payload[0]["data"][0]
    return [Session.from_row(dict(zip(cols, values))) for values in zip(*data)]


def is_target(s: Session) -> bool:
    return s.program == TARGET_PROGRAM and date.fromisoformat(s.date).weekday() in TARGET_WEEKDAYS


@dataclass(frozen=True)
class Alerted:
    """A session we emailed about, kept so we can say if it disappears."""

    session: Session
    found_at: str  # when it was first seen, e.g. "2026-10-03T14:15-07:00"


@dataclass
class State:
    seen: dict[str, str]  # event id -> date
    seen_through: str  # latest date visible in a previous check
    alerted: dict[str, Alerted] = field(default_factory=dict)  # event id -> details


def load_state(path: Path) -> State | None:
    """Return the stored state, or None if there is no baseline yet."""
    if not path.exists():
        return None
    raw = json.loads(path.read_text())
    alerted = {k: Alerted(Session(**v["session"]), v["found_at"]) for k, v in raw.get("alerted", {}).items()}
    return State(seen=raw["seen"], seen_through=raw["seen_through"], alerted=alerted)


def save_state(path: Path, state: State) -> None:
    raw = {
        "seen_through": state.seen_through,
        "alerted": {k: asdict(v) for k, v in sorted(state.alerted.items())},
        "seen": dict(sorted(state.seen.items())),
    }
    path.write_text(json.dumps(raw, indent=1) + "\n")


def update(state: State | None, sessions: list[Session], now: str) -> tuple[list[Session], list[Alerted], State]:
    """Return (newly added target sessions, alerted sessions now gone, new state).

    `now` is the check time, recorded as each new session's discovery time.
    """
    targets = [s for s in sessions if is_target(s)]
    latest = max((s.date for s in sessions), default="")
    if state is None:
        return [], [], State({s.event_id: s.date for s in targets}, latest)

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

    # Sessions we alerted about that are no longer listed, though their date
    # is still in the window. Each is reported once, then dropped.
    current = {s.event_id for s in sessions}
    gone = []
    alerted = {}
    for k, a in state.alerted.items():
        if a.session.date < earliest:
            continue
        if k in current:
            alerted[k] = a
        else:
            gone.append(a)
    gone.sort(key=lambda a: (a.session.date, a.session.start, a.session.name))
    alerted.update({s.event_id: Alerted(s, now) for s in added})

    return added, gone, State(seen, max(state.seen_through, latest), alerted)
