import os
import smtplib
from datetime import date, datetime
from email.message import EmailMessage

from .classes import Session

BOOKING_URL = "https://apps.daysmartrecreation.com/dash/x/#/online/copa/login"


def _time(hhmm: str) -> str:
    return datetime.strptime(hhmm, "%H:%M").strftime("%I:%M %p").lstrip("0")


def format_email(added: list[Session]) -> EmailMessage:
    msg = EmailMessage()
    noun = "session" if len(added) == 1 else "sessions"
    msg["Subject"] = f"COPA: {len(added)} new 12-19 weekend {noun}"
    lines = []
    for s in added:
        day = date.fromisoformat(s.date).strftime("%a %b %-d")
        lines.append(f"- {day}, {_time(s.start)}-{_time(s.end)}: {s.name}")
    lines += ["", f"Book on DaySmart: {BOOKING_URL}"]
    msg.set_content("\n".join(lines))
    return msg


def send_email(msg: EmailMessage) -> None:
    user = os.environ["GMAIL_USER"]
    msg["From"] = user
    msg["To"] = os.environ.get("ALERT_TO") or user
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(user, os.environ["GMAIL_APP_PASSWORD"])
        smtp.send_message(msg)
