from __future__ import annotations

import argparse
import datetime as dt
import logging
import sys
from pathlib import Path

from gpxtrackposter import (
    circular_drawer,
    github_drawer,
    grid_drawer,
    month_of_life_drawer,
    poster,
    track_loader,
)
from gpxtrackposter.exceptions import ParameterError, PosterError
from pushup_page.config import ASSETS_DIR, SQL_FILE
from pushup_page.stats import activity_dates_from_tracks, calculate_streak

# from flopp great repo
__app_name__ = "create_poster"
__app_author__ = "flopp.net"


def calculate_track_streak(tracks) -> int:
    return calculate_streak(activity_dates_from_tracks(tracks))


def main():
    """Handle command line arguments and call other modules as needed."""

    p = poster.Poster()
    drawers = {
        "grid": grid_drawer.GridDrawer(p),
        "circular": circular_drawer.CircularDrawer(p),
        "github": github_drawer.GithubDrawer(p),
        "monthoflife": month_of_life_drawer.MonthOfLifeDrawer(p),
    }

    args_parser = argparse.ArgumentParser()
    current_year = dt.date.today().year
    args_parser.add_argument(
        "--output",
        metavar="FILE",
        type=str,
        default=str(ASSETS_DIR / f"github_{current_year}.svg"),
        help=f'Name of generated SVG image file (default: "assets/github_{current_year}.svg").',
    )
    args_parser.add_argument(
        "--language",
        metavar="LANGUAGE",
        type=str,
        default="",
        help="Language (default: english).",
    )
    args_parser.add_argument(
        "--year",
        metavar="YEAR",
        type=str,
        default="all",
        help='Filter tracks by year; "NUM", "NUM-NUM", "all" (default: all years)',
    )
    args_parser.add_argument(
        "--title", metavar="TITLE", type=str, help="Title to display."
    )
    args_parser.add_argument(
        "--athlete",
        metavar="NAME",
        type=str,
        default="Andy963",
        help='Athlete name to display (default: "Andy963").',
    )
    types = '", "'.join(drawers.keys())
    args_parser.add_argument(
        "--type",
        metavar="TYPE",
        default="grid",
        choices=drawers.keys(),
        help=f'Type of poster to create (default: "grid", available: "{types}").',
    )
    args_parser.add_argument(
        "--background-color",
        dest="background_color",
        metavar="COLOR",
        type=str,
        default="#222222",
        help='Background color of poster (default: "#222222").',
    )
    args_parser.add_argument(
        "--track-color",
        dest="track_color",
        metavar="COLOR",
        type=str,
        default="#4DD2FF",
        help='Color of tracks (default: "#4DD2FF").',
    )
    args_parser.add_argument(
        "--track-color2",
        dest="track_color2",
        metavar="COLOR",
        type=str,
        help="Secondary color of tracks (default: none).",
    )
    args_parser.add_argument(
        "--text-color",
        dest="text_color",
        metavar="COLOR",
        type=str,
        default="#FFFFFF",
        help='Color of text (default: "#FFFFFF").',
    )
    args_parser.add_argument(
        "--units",
        dest="units",
        metavar="UNITS",
        type=str,
        choices=["metric", "imperial"],
        default="metric",
        help='Distance units; "metric", "imperial" (default: "metric").',
    )
    args_parser.add_argument(
        "--verbose", dest="verbose", action="store_true", help="Verbose logging."
    )
    args_parser.add_argument("--logfile", dest="logfile", metavar="FILE", type=str)
    args_parser.add_argument(
        "--min-count",
        dest="min_count",
        metavar="COUNT",
        type=int,
        default=1,
        help="min count for track filter",
    )
    args_parser.add_argument(
        "--use-localtime",
        dest="use_localtime",
        action="store_true",
        help="Use utc time or local time",
    )

    args_parser.add_argument(
        "--from-db",
        dest="from_db",
        action="store_true",
        help="activities db file",
    )

    args_parser.add_argument(
        "--github-style",
        dest="github_style",
        metavar="GITHUB_STYLE",
        type=str,
        default="align-firstday",
        help='github svg style; "align-firstday", "align-monday" (default: "align-firstday").',
    )

    args_parser.add_argument(
        "--workers",
        dest="workers",
        metavar="WORKERS",
        type=int,
        default=None,
        help="Number of workers for parallel processing.",
    )
    args_parser.add_argument(
        "--with-animation",
        dest="with_animation",
        action="store_true",
        help="Add animation to the poster.",
    )
    args_parser.add_argument(
        "--animation-time",
        dest="animation_time",
        metavar="SECONDS",
        type=int,
        default=30,
        help="Animation time in seconds.",
    )

    for _, drawer in drawers.items():
        drawer.create_args(args_parser)

    args = args_parser.parse_args()

    for _, drawer in drawers.items():
        drawer.fetch_args(args)

    log = logging.getLogger("gpxtrackposter")
    log.setLevel(logging.INFO if args.verbose else logging.ERROR)
    if args.logfile:
        handler = logging.FileHandler(args.logfile)
        log.addHandler(handler)

    loader = track_loader.TrackLoader(args.workers)
    if args.use_localtime:
        loader.use_local_time = True
    if not loader.year_range.parse(args.year):
        raise ParameterError(f"Bad year range: {args.year}.")

    loader.set_min_count(args.min_count)

    # Only support loading tracks from DB
    tracks = loader.load_tracks_from_db(SQL_FILE, args.type == "grid")

    if not tracks:
        return

    # Print streak value
    streak = calculate_track_streak(tracks)
    print(f"Current push-up streak: {streak} days")

    is_circular = args.type == "circular"
    is_mol = args.type == "monthoflife"

    if not is_circular and not is_mol:
        print(
            f"Creating poster of type {args.type} with {len(tracks)} tracks and storing it in file {args.output}..."
        )
    p.set_language(args.language)
    p.athlete = args.athlete
    if args.title:
        p.title = args.title
    else:
        p.title = p.trans("MY TRACKS")

    p.colors = {
        "background": args.background_color,
        "track": args.track_color,
        "track2": args.track_color2 or args.track_color,
        "text": args.text_color,
    }
    p.units = args.units
    p.with_animation = args.with_animation
    p.animation_time = args.animation_time
    p.set_tracks(tracks)
    # circular not add footer and header
    p.drawer_type = "plain" if is_circular else "title"
    if is_mol:
        p.drawer_type = "monthoflife"
    if args.type == "github":
        p.height = 55 + p.years.count() * 43
    p.github_style = args.github_style

    if args.type == "circular":
        if args.background_color == "#222222":
            p.colors["background"] = "#1a1a1a"
        if args.track_color == "#4DD2FF":
            p.colors["track"] = "red"
        if args.text_color == "#FFFFFF":
            p.colors["text"] = "#e1ed5e"

    # for special circular
    if is_circular:
        years = list(p.years.iter())[:]
        output_path = Path(args.output)
        output_dir = (
            output_path.parent if output_path.parent != Path(".") else ASSETS_DIR
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        for y in years:
            p.years.from_year, p.years.to_year = y, y
            # may be refactor
            p.set_tracks(tracks)
            p.draw(drawers[args.type], str(output_dir / f"year_{y}.svg"))
    else:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        p.draw(drawers[args.type], args.output)


if __name__ == "__main__":
    try:
        # generate svg
        main()
    except PosterError as e:
        print(e)
        sys.exit(1)
