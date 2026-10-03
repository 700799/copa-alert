# copa-alert

Emails you when a new class for ages 12–18 appears on a Friday, Saturday or
Sunday on the [COPA membership scheduling page](https://copastc.com/membership-scheduling/).
Changes in enrollment or spots left never trigger an alert.

A GitHub Actions workflow runs every 90 minutes. It signs in with a headless
browser, reads the schedule, and compares the weekend 12–18 classes with
`seen.json`. That file holds hashes, not class details, so this public repo
doesn't publish the schedule. The first run only records a baseline.

## Status

The login and page-reading steps in `copa_alert/scraper.py` are still TODO.
The site couldn't be reached while this was written.

## Setup

1. Add these under **Settings → Secrets and variables → Actions → Secrets**:
   - `COPA_ACCESS_CODE`: the code used to sign in
   - `GMAIL_USER`: the Gmail address that sends the alert
   - `GMAIL_APP_PASSWORD`: a Gmail [app password](https://myaccount.google.com/apppasswords) (needs 2-step verification)
   - `ALERT_TO` (optional): where to send alerts; defaults to `GMAIL_USER`
2. Run **Actions → Check for new classes → Run workflow** once to check it works.
3. Turn on the schedule: under **Settings → Secrets and variables → Actions →
   Variables**, add `ALERTS_ENABLED` with value `true`.

If a run finds no classes at all (for example, the login broke), it fails
without changing `seen.json`, and GitHub emails you about the failed run.

## Tests

```
pip install pytest
python -m pytest
```
