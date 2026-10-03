from copa_alert.classes import (
    ClassListing,
    find_new,
    is_target,
    load_seen,
    parse_age_range,
    save_seen,
)


def make(name="Teen Hip Hop", ages="Ages 12-18", day="Saturday", start_time="10:00 AM", **kw):
    return ClassListing(name=name, ages=ages, day=day, start_time=start_time, **kw)


def test_parse_age_range():
    assert parse_age_range("Ages 12-18") == (12, 18)
    assert parse_age_range("12 – 18 yrs") == (12, 18)
    assert parse_age_range("13 to 17") == (13, 17)
    assert parse_age_range("13+") == (13, 99)
    assert parse_age_range("All levels") is None


def test_targets_weekend_teen_classes_only():
    assert is_target(make(day="Friday"))
    assert is_target(make(day="Sat"))
    assert is_target(make(day="sunday", ages="14-16"))
    assert not is_target(make(day="Thursday"))
    assert not is_target(make(ages="Ages 8-12"))
    assert not is_target(make(ages="Adults 18+"))
    assert not is_target(make(ages="Open"))


def test_key_ignores_formatting_but_not_identity():
    assert make().key() == make(name="  teen  hip hop ", day="Sat").key()
    assert make().key() != make(start_time="11:00 AM").key()


def test_find_new_reports_only_unseen_targets():
    existing = make()
    seen = {existing.key()}
    added = make(name="Teen Contemporary")
    weekday = make(name="Teen Ballet", day="Monday")
    assert find_new([existing, added, added, weekday], seen) == [added]


def test_seen_round_trip(tmp_path):
    path = tmp_path / "seen.json"
    assert load_seen(path) is None
    save_seen(path, {"b", "a"})
    assert load_seen(path) == {"a", "b"}
