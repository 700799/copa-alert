from copa_alert.classes import Alerted, Session
from copa_alert.notify import format_email


def test_email_is_compact_and_shows_times():
    new = Session("2", "12 - 19yrs", "SC: SoccerBot 360 (LV1)", "2026-10-11", "09:30", "10:00", "3", "7800")
    old = Session("5", "12 - 19yrs", "SC: Finishing (LV3)", "2026-10-10", "08:30", "09:00", "0")
    msg = format_email([new], [Alerted(old, "2026-10-02T11:45-07:00")], "2026-10-03T14:15-07:00")
    assert msg["Subject"] == "COPA 12-19 weekend: 1 new, 1 gone"
    assert msg.get_content().splitlines() == [
        "NEW · found Sat 10/3 2:15 PM",
        "  Sun 10/11 9:30 AM-10:00 AM · SC: SoccerBot 360 (LV1) · 3 spots",
        "    Register: https://apps.daysmartrecreation.com/dash/x/copa/group/register/7800",
        "",
        "GONE · no longer listed at Sat 10/3 2:15 PM",
        "  Sat 10/10 8:30 AM-9:00 AM · SC: Finishing (LV3) · found Fri 10/2 11:45 AM",
        "",
        "All sessions: https://apps.daysmartrecreation.com/dash/x/#/online/copa/login",
    ]
