from copa_alert.classes import Session, State, is_target, load_state, parse_schedule, save_state, update

TEEN = "12 - 19yrs"


def make(event_id, day="2026-10-10", program=TEEN, name="SC: SoccerBot 360 (LV1)", start="08:30"):
    return Session(event_id=event_id, program=program, name=name, date=day, start=start, end="09:00")


def test_parse_schedule():
    payload = [
        {
            "cols": ["s_eventid", "programname", "teamname", "leaguedesc", "start_date", "s_eventstart", "s_eventend", "spots_left"],
            "data": [[["1", "2"], [TEEN, "6 - 8yrs"], ["SC: Finishing (LV3)", None], ["x", "Soccer 6-8"], ["2026-10-10", "2026-10-11"], ["2026-10-10T09:00:00.000Z", "2026-10-11T10:00:00.000Z"], ["2026-10-10T09:30:00.000Z", "2026-10-11T10:45:00.000Z"], ["3", "1"]]],
        }
    ]
    assert parse_schedule(payload) == [
        Session("1", TEEN, "SC: Finishing (LV3)", "2026-10-10", "09:00", "09:30"),
        Session("2", "6 - 8yrs", "Soccer 6-8", "2026-10-11", "10:00", "10:45"),
    ]


def test_targets_weekend_teen_sessions_only():
    assert is_target(make("1", day="2026-10-09"))  # Friday
    assert is_target(make("1", day="2026-10-10"))  # Saturday
    assert is_target(make("1", day="2026-10-11"))  # Sunday
    assert not is_target(make("1", day="2026-10-08"))  # Thursday
    assert not is_target(make("1", program="9 - 11yrs"))


def test_first_run_is_baseline():
    added, state = update(None, [make("1"), make("2", program="9 - 11yrs")])
    assert added == []
    assert state.seen == {"1": "2026-10-10"}
    assert state.seen_through == "2026-10-10"


def test_alerts_only_for_sessions_added_to_already_visible_dates():
    state = State({"1": "2026-10-10"}, seen_through="2026-10-15")
    added_mid_window = make("2", day="2026-10-11")
    rolled_into_view = make("3", day="2026-10-17")
    weekday = make("4", day="2026-10-13")
    sessions = [make("1"), added_mid_window, rolled_into_view, weekday]
    added, new = update(state, sessions)
    assert added == [added_mid_window]
    assert set(new.seen) == {"1", "2", "3"}
    assert new.seen_through == "2026-10-17"


def test_spots_changing_or_session_reappearing_is_not_new():
    state = State({"1": "2026-10-10"}, seen_through="2026-10-15")
    # Session 1 vanished from one check (e.g. full) and came back.
    _, state = update(state, [make("9", day="2026-10-04", program="9 - 11yrs")])
    added, _ = update(state, [make("1")])
    assert added == []


def test_past_dates_are_pruned():
    state = State({"old": "2026-10-01", "1": "2026-10-10"}, seen_through="2026-10-15")
    _, new = update(state, [make("0", day="2026-10-04", program="9 - 11yrs"), make("1")])
    assert set(new.seen) == {"1"}


def test_state_round_trip(tmp_path):
    path = tmp_path / "seen.json"
    assert load_state(path) is None
    save_state(path, State({"2": "2026-10-11", "1": "2026-10-10"}, "2026-10-15"))
    assert load_state(path) == State({"1": "2026-10-10", "2": "2026-10-11"}, "2026-10-15")
