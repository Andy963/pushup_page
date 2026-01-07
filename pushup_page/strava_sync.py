from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import sqlite3

import stravalib

from generator import Generator
from pushup_page.config import CSV_PATH, SQL_FILE
from pushup_page.storage import get_latest_activity_datetime, open_session

DEFAULT_START_DATE = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)


def export_activities_to_csv(
    db_path: str = SQL_FILE, csv_path: str = str(CSV_PATH)
) -> None:
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM activities")
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        writer.writerows(rows)


def resolve_strava_secrets(args: argparse.Namespace) -> tuple[str, str, str]:
    client_id = args.client_id or args.client_id_arg or os.getenv("CLIENT_ID")
    client_secret = (
        args.client_secret or args.client_secret_arg or os.getenv("CLIENT_SECRET")
    )
    refresh_token = (
        args.refresh_token or args.refresh_token_arg or os.getenv("REFRESH_TOKEN")
    )

    missing = [
        name
        for name, value in [
            ("CLIENT_ID", client_id),
            ("CLIENT_SECRET", client_secret),
            ("REFRESH_TOKEN", refresh_token),
        ]
        if not value
    ]
    if missing:
        raise SystemExit(
            "Missing Strava secrets. Provide them via CLI args or env vars: "
            + ", ".join(missing)
        )

    return client_id, client_secret, refresh_token


def run_strava_sync(
    *,
    client_id: str,
    client_secret: str,
    refresh_token: str,
    start_date: dt.datetime | None = None,
    export_csv: bool = True,
) -> None:
    generator = Generator(SQL_FILE)
    generator.set_strava_config(client_id, client_secret, refresh_token)

    if start_date is None:
        with open_session() as session:
            last_activity = get_latest_activity_datetime(session)
        start_date = (
            last_activity + dt.timedelta(seconds=1)
            if last_activity is not None
            else DEFAULT_START_DATE
        )

    print(f"Syncing activities from {start_date}...")
    try:
        try:
            generator.sync(False, start_date=start_date)
        except stravalib.exc.RateLimitExceeded:
            print("Strava API rate limit exceeded. Stopping sync.")
    finally:
        generator.close()

    if export_csv:
        export_activities_to_csv()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Sync push-up activities from Strava.")

    parser.add_argument("--client-id", dest="client_id", help="Strava client id")
    parser.add_argument(
        "--client-secret", dest="client_secret", help="Strava client secret"
    )
    parser.add_argument(
        "--refresh-token", dest="refresh_token", help="Strava refresh token"
    )
    parser.add_argument(
        "client_id_arg", nargs="?", help="Strava client id (legacy positional)"
    )
    parser.add_argument(
        "client_secret_arg",
        nargs="?",
        help="Strava client secret (legacy positional)",
    )
    parser.add_argument(
        "refresh_token_arg",
        nargs="?",
        help="Strava refresh token (legacy positional)",
    )

    parser.add_argument(
        "--start-date",
        dest="start_date",
        metavar="ISO8601",
        help='Override sync start date (e.g. "2025-01-01T00:00:00+00:00").',
    )
    parser.add_argument(
        "--no-export-csv",
        dest="export_csv",
        action="store_false",
        help="Skip exporting DB rows to pushup_data.csv.",
    )

    args = parser.parse_args(argv)
    client_id, client_secret, refresh_token = resolve_strava_secrets(args)

    start_date = dt.datetime.fromisoformat(args.start_date) if args.start_date else None

    run_strava_sync(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        start_date=start_date,
        export_csv=args.export_csv,
    )


if __name__ == "__main__":
    main()
