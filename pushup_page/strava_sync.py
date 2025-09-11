import argparse
import sys
import datetime
import stravalib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dateutil.parser import parse

from pushup_page.config import SQL_FILE
from generator import Generator
from generator.db import Activity
from pushup_page.data_to_csv import main as generate_csv


def get_last_activity_date():
    """Fetches the start_date of the most recent activity from the database."""
    engine = create_engine(f"sqlite:///{SQL_FILE}")
    Session = sessionmaker(bind=engine)
    session = Session()
    latest_activity = session.query(Activity).order_by(Activity.start_date.desc()).first()
    session.close()
    if latest_activity:
        # Add a small buffer to avoid re-fetching the same activity
        return parse(latest_activity.start_date) + datetime.timedelta(seconds=1)
    return None


def run_strava_sync(client_id, client_secret, refresh_token):
    generator = Generator(SQL_FILE)
    generator.set_strava_config(client_id, client_secret, refresh_token)

    start_date = get_last_activity_date()
    if not start_date:
        start_date = datetime.datetime(2025, 1, 1)

    print(f"Syncing activities from {start_date}...")
    try:
        generator.sync(False, start_date=start_date)
    except stravalib.exc.RateLimitExceeded:
        print("Strava API rate limit exceeded. Stopping sync.")

    generate_csv()


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Error: Missing secrets in script arguments.")
        sys.exit(1)
    print("All secrets provided as arguments.")
    parser = argparse.ArgumentParser()
    parser.add_argument("client_id", help="strava client id")
    parser.add_argument("client_secret", help="strava client secret")
    parser.add_argument("refresh_token", help="strava refresh token")
    options = parser.parse_args()
    run_strava_sync(
        options.client_id,
        options.client_secret,
        options.refresh_token,
    )
