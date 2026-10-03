# copa-alert

Emails you when a new 12–19 session is added on a Friday, Saturday or Sunday
to the [COPA schedule](https://copastc.com/membership-scheduling/). Changes in
spots left never trigger an alert.

A GitHub Actions workflow runs every 90 minutes. It opens the public schedule
(an embedded Retool app, no login needed) in a headless browser, reads the
sessions the page loads, and compares the 12–19 weekend sessions with
`seen.json`.

The schedule only shows about two weeks ahead, so new dates come into view
every day. To avoid an email for the regular schedule each week, a session
counts as added only when it appears on a date an earlier check could
already see. The first run only records a baseline.

The email lists new sessions with the time they were found and spots left.
If a session you were emailed about later disappears from the schedule (for
example, it filled up or was cancelled) while its date is still listed, the
next email lists it under GONE, once.

## Setup

1. Add these under **Settings → Secrets and variables → Actions → Secrets**:
   - `GMAIL_USER`: the Gmail address that sends the alert
   - `GMAIL_APP_PASSWORD`: a Gmail [app password](https://myaccount.google.com/apppasswords) (needs 2-step verification)
   - `ALERT_TO` (optional): where to send alerts; defaults to `GMAIL_USER`
2. Run **Actions → Check for new classes → Run workflow** once to record the
   baseline.

If a run finds no sessions at all (for example, the page changed), it fails
without changing `seen.json`, and GitHub emails you about the failed run.

## Running locally

```
pip install -r requirements.txt pytest
python -m playwright install chromium
python -m pytest
python -m copa_alert --dry-run   # prints what would be emailed; sends and saves nothing
```
