import argparse
import sys
import datetime
import stravalib

from pushup_page.config import SQL_FILE
from generator import Generator
from pushup_page.data_to_csv import main as generate_csv


def run_strava_sync(
    client_id,
    client_secret,
    refresh_token,
):
    generator = Generator(SQL_FILE)
    generator.set_strava_config(client_id, client_secret, refresh_token)

    # Sync from May 11, 2025
    start_date = datetime.datetime(*(2025, 8, 20, 6, 39, 0))
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
