from __future__ import annotations

import datetime as dt
from collections.abc import Iterable
from typing import Any

from dateutil.parser import parse


def calculate_streak(dates: Iterable[dt.date], *, today: dt.date | None = None) -> int:
    unique_dates = sorted(set(dates), reverse=True)
    if not unique_dates:
        return 0

    if today is None:
        today = dt.date.today()

    yesterday = today - dt.timedelta(days=1)

    if unique_dates[0] == today:
        streak = 1
        expected = yesterday
        idx = 1
    elif unique_dates[0] == yesterday:
        streak = 0
        expected = yesterday
        idx = 0
    else:
        return 0

    while idx < len(unique_dates) and unique_dates[idx] == expected:
        streak += 1
        expected -= dt.timedelta(days=1)
        idx += 1

    return streak


def activity_dates_from_tracks(tracks: Iterable[Any]) -> list[dt.date]:
    dates: list[dt.date] = []
    for track in tracks:
        if hasattr(track, "start_time") and callable(track.start_time):
            try:
                dates.append(track.start_time().date())
                continue
            except Exception:
                pass
        start_date = getattr(track, "start_date", None)
        if start_date is None:
            continue
        if isinstance(start_date, dt.datetime):
            dates.append(start_date.date())
        elif isinstance(start_date, dt.date):
            dates.append(start_date)
    return dates


def activity_dates_from_start_date_strings(start_dates: Iterable[str]) -> list[dt.date]:
    dates: list[dt.date] = []
    for start_date in start_dates:
        if not start_date:
            continue
        try:
            dates.append(dt.datetime.fromisoformat(start_date).date())
        except ValueError:
            try:
                dates.append(parse(start_date).date())
            except (ValueError, TypeError):
                continue
    return dates
