from copa_alert.classes import Alerted, Session
from copa_alert.log_page import record, render

NOW = "2026-10-03T14:15-07:00"


def test_events_newest_first_and_rendered():
    new = Session("2", "12 - 19yrs", "SC: <SoccerBot>", "2026-10-11", "09:30", "10:00", "1", "7800")
    old = Session("5", "12 - 19yrs", "SC: Finishing (LV3)", "2026-10-10", "08:30", "09:00", "0", "7701")
    events = record([], [old], [], "2026-10-02T11:45-07:00")
    events = record(events, [new], [Alerted(old, "2026-10-02T11:45-07:00")], NOW)
    assert [(e["kind"], e["session"]["event_id"]) for e in events] == [("new", "2"), ("gone", "5"), ("new", "5")]

    html = render(events)
    assert "SC: &lt;SoccerBot&gt;" in html
    assert "found Sat 10/3 2:15 PM · 1 spot" in html
    assert "/group/register/7800" in html
    assert "gone Sat 10/3 2:15 PM · found Fri 10/2 11:45 AM" in html


def test_empty_log():
    assert "No changes yet." in render([])
