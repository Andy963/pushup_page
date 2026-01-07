from __future__ import annotations

import datetime as dt
import re
import sys
from typing import Iterable

import arrow
import stravalib
from sqlalchemy import func

from .db import Activity, init_db, update_or_create_activity

COUNT_RE = re.compile(r"Total Reps: (\d+)")
AVG_RE = re.compile(r"Average Time per Push-Up: (\d+(\.\d+)?)s")
CALORIES_RE = re.compile(r"Burned Calories: (\d+(\.\d+)?)")


class Generator:
    def __init__(self, db_path: str):
        self.client = stravalib.Client()
        self.session = init_db(db_path)

        self.client_id = ""
        self.client_secret = ""
        self.refresh_token = ""

    def close(self) -> None:
        self.session.close()

    def set_strava_config(self, client_id: str, client_secret: str, refresh_token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token

    def check_access(self) -> None:
        response = self.client.refresh_access_token(
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=self.refresh_token,
        )
        # Update the authdata object
        self.access_token = response["access_token"]
        self.refresh_token = response["refresh_token"]

        self.client.access_token = response["access_token"]
        print("Access ok")

    def sync(self, force: bool, start_date: dt.datetime | None = None) -> None:
        """
        Sync activities means sync from strava
        """
        self.check_access()

        print("Start syncing")
        if start_date:
            filters = {"after": start_date}
        else:
            last_activity_date_str = self.session.query(
                func.max(Activity.start_date)
            ).scalar()
            print("last activity date:", last_activity_date_str)
            if last_activity_date_str:
                last_activity_date = arrow.get(last_activity_date_str)
                last_activity_date = last_activity_date.shift(days=-7)
                filters = {"after": last_activity_date.datetime}
            else:
                filters = {"before": dt.datetime.now(dt.timezone.utc)}
        activities = list(self.client.get_activities(**filters, limit=10))

        for activity in activities:
            print("activity", activity.id, activity.start_date)
            if "push-ups" not in str(activity.name).lower():
                continue

            activity_detail = self.client.get_activity(activity.id)
            # description='Total Reps: 57\nAverage Time per Push-Up: 0.67s\nBurned Calories: 18.06\n\nData from Puuush App\nhttps://puuush.wsfu.co/andyzhou'
            desc = activity_detail.description
            # get count ,avg, coliries, from description
            if not desc or "Total Reps" not in desc:
                print(f"skip activity {activity.id} since no count found")
                continue

            count_match = COUNT_RE.search(desc)
            avg_match = AVG_RE.search(desc)
            calories_match = CALORIES_RE.search(desc)

            count = int(count_match.group(1)) if count_match else 0
            avg_time = float(avg_match.group(1)) if avg_match else 0.0
            calories = float(calories_match.group(1)) if calories_match else 0.0

            created = update_or_create_activity(
                self.session, activity_detail, count, avg_time, calories
            )
            if created:
                sys.stdout.write("+")
            else:
                sys.stdout.write(".")
            sys.stdout.flush()
        self.session.commit()

    def load(self) -> list[dict]:
        activities: Iterable[Activity] = self.session.query(Activity).order_by(
            Activity.start_date
        )
        return [activity.to_dict() for activity in activities]
