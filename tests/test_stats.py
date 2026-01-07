import datetime as dt

from pushup_page.stats import (
    activity_dates_from_start_date_strings,
    activity_dates_from_tracks,
    calculate_streak,
)


def test_calculate_streak_empty() -> None:
    assert calculate_streak([]) == 0


def test_calculate_streak_today_only() -> None:
    today = dt.date(2025, 1, 10)
    assert calculate_streak([today], today=today) == 1


def test_calculate_streak_yesterday_only() -> None:
    today = dt.date(2025, 1, 10)
    assert calculate_streak([today - dt.timedelta(days=1)], today=today) == 1


def test_calculate_streak_consecutive() -> None:
    today = dt.date(2025, 1, 10)
    dates = [today, today - dt.timedelta(days=1), today - dt.timedelta(days=2)]
    assert calculate_streak(dates, today=today) == 3


def test_calculate_streak_gap_breaks() -> None:
    today = dt.date(2025, 1, 10)
    dates = [today, today - dt.timedelta(days=2), today - dt.timedelta(days=3)]
    assert calculate_streak(dates, today=today) == 1


def test_calculate_streak_duplicates_ok() -> None:
    today = dt.date(2025, 1, 10)
    dates = [today, today, today - dt.timedelta(days=1)]
    assert calculate_streak(dates, today=today) == 2


def test_activity_dates_from_start_date_strings_parses() -> None:
    dates = activity_dates_from_start_date_strings(
        [
            "2025-01-10T00:00:00+00:00",
            "2025-01-09 00:00:00+00:00",
        ]
    )
    assert sorted(dates) == [dt.date(2025, 1, 9), dt.date(2025, 1, 10)]


class _Track:
    def __init__(self, start: dt.datetime) -> None:
        self._start = start

    def start_time(self) -> dt.datetime:
        return self._start


def test_activity_dates_from_tracks_uses_start_time() -> None:
    tracks = [_Track(dt.datetime(2025, 1, 10, 1, 2, 3, tzinfo=dt.timezone.utc))]
    assert activity_dates_from_tracks(tracks) == [dt.date(2025, 1, 10)]
