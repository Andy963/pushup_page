import datetime as dt

from generator.db import Activity, init_db
from pushup_page.storage import get_latest_activity_datetime


def test_get_latest_activity_datetime(tmp_path) -> None:
    db_path = tmp_path / "data.db"
    session = init_db(str(db_path))
    try:
        session.add(
            Activity(
                run_id=1,
                name="push-ups",
                start_date="2025-01-01T00:00:00+00:00",
                elapsed_time=10,
                count=10,
                avg_time=1.0,
                calories=5.0,
            )
        )
        session.add(
            Activity(
                run_id=2,
                name="push-ups",
                start_date="2025-01-02T00:00:00+00:00",
                elapsed_time=10,
                count=10,
                avg_time=1.0,
                calories=5.0,
            )
        )
        session.commit()

        latest = get_latest_activity_datetime(session)
        assert latest is not None
        assert latest.date() == dt.date(2025, 1, 2)
    finally:
        session.close()
