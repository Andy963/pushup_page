import argparse
import os
import sys

from .config import SQL_FILE
from .data_to_csv import main as generate_csv
from ..generator import Generator


def run_strava_sync(
    client_id,
    client_secret,
    refresh_token,
):
    generator = Generator(SQL_FILE)
    generator.set_strava_config(client_id, client_secret, refresh_token)
    generator.sync(False)
    generate_csv()


if __name__ == "__main__":
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