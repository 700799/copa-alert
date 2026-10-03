import os
import smtplib
from datetime import date, datetime
from email.message import EmailMessage

from .classes import Alerted, Session

BOOKING_URL = "https://apps.daysmartrecreation.com/dash/x/#/online/copa/login"


def _time(hhmm: str) -> str:
    return datetime.strptime(hhmm, "%H:%M").strftime("%I:%M %p").lstrip("0")


def _when(iso: str) -> str:
    """Check time, e.g. "Sat 10/3 2:15 PM"."""
    t = datetime.fromisoformat(iso)
    return f"{t:%a} {t.month}/{t.day} {t:%I:%M %p}".replace(" 0", " ")


def _session(s: Session) -> str:
    d = date.fromisoformat(s.date)
    return f"{d:%a} {d.month}/{d.day} {_time(s.start)}-{_time(s.end)} · {s.name}"


def format_email(added: list[Session], gone: list[Alerted], now: str) -> EmailMessage:
    parts = []
    if added:
        parts.append(f"{len(added)} new")
    if gone:
        parts.append(f"{len(gone)} gone")
    msg = EmailMessage()
    msg["Subject"] = f"COPA 12-19 weekend: {', '.join(parts)}"

    lines = []
    if added:
        lines.append(f"NEW · found {_when(now)}")
        for s in added:
            spots = f" · {s.spots_left} spot{'' if s.spots_left == '1' else 's'}" if s.spots_left else ""
            lines.append(f"  {_session(s)}{spots}")
        lines.append("")
    if gone:
        lines.append(f"GONE · no longer listed at {_when(now)}")
        for a in gone:
            lines.append(f"  {_session(a.session)} · found {_when(a.found_at)}")
        lines.append("")
    lines.append(f"Book: {BOOKING_URL}")
    msg.set_content("\n".join(lines))
    return msg


def send_email(msg: EmailMessage) -> None:
    user = os.environ["GMAIL_USER"]
    msg["From"] = user
    msg["To"] = os.environ.get("ALERT_TO") or user
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(user, os.environ["GMAIL_APP_PASSWORD"])
        smtp.send_message(msg)
