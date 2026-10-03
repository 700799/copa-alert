import os
import smtplib
from email.message import EmailMessage

from .classes import ClassListing


def format_email(new: list[ClassListing]) -> EmailMessage:
    msg = EmailMessage()
    noun = "class" if len(new) == 1 else "classes"
    msg["Subject"] = f"COPA: {len(new)} new 12-18 weekend {noun}"
    lines = []
    for c in new:
        when = " ".join(filter(None, [c.day, c.date, c.start_time]))
        extra = f" with {c.instructor}" if c.instructor else ""
        lines.append(f"- {c.name} ({c.ages}): {when}{extra}")
    lines.append("")
    lines.append("Book: https://copastc.com/membership-scheduling/")
    msg.set_content("\n".join(lines))
    return msg


def send_email(msg: EmailMessage) -> None:
    user = os.environ["GMAIL_USER"]
    msg["From"] = user
    msg["To"] = os.environ.get("ALERT_TO") or user
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(user, os.environ["GMAIL_APP_PASSWORD"])
        smtp.send_message(msg)
