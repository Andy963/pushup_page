from __future__ import annotations

import datetime as dt
from contextlib import contextmanager
from typing import Iterator

from dateutil.parser import parse
from sqlalchemy.orm import Session

from generator.db import Activity, init_db
from pushup_page.config import DB_PATH


@contextmanager
def open_session(db_path: str | None = None) -> Iterator[Session]:
    session = init_db(db_path or str(DB_PATH))
    try:
        yield session
    finally:
        session.close()


def get_latest_activity_datetime(session: Session) -> dt.datetime | None:
    latest = session.query(Activity).order_by(Activity.start_date.desc()).first()
    if not latest or not latest.start_date:
        return None
    try:
        return dt.datetime.fromisoformat(latest.start_date)
    except ValueError:
        return parse(latest.start_date)


def list_activities(session: Session) -> list[Activity]:
    return session.query(Activity).order_by(Activity.start_date).all()
