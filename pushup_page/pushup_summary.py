import svgwrite
import datetime
from collections import defaultdict
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dateutil.parser import parse
from generator.db import Activity, Base


# Database setup
SQL_FILE = "data.db"
engine = create_engine(f"sqlite:///{SQL_FILE}")
Session = sessionmaker(bind=engine)


def get_data():
    """Fetches activity data from the database."""
    session = Session()
    activities = session.query(Activity).order_by(Activity.start_date).all()
    session.close()
    return activities


def process_data(activities):
    """Processes activities to get yearly, monthly, and weekly totals."""
    yearly = defaultdict(int)
    monthly = defaultdict(int)
    weekly = defaultdict(int)

    for act in activities:
        if act.start_date and act.count:
            try:
                date = parse(act.start_date)
            except (ValueError, TypeError):
                print(f"Could not parse date: {act.start_date}")
                continue

            yearly[date.year] += act.count
            monthly[date.strftime("%Y-%m")] += act.count
            # Group by the date of the first day of the week (Sunday)
            first_day_of_week = date - datetime.timedelta(days=(date.weekday() + 1) % 7)
            weekly[first_day_of_week.strftime("%Y-%m-%d")] += act.count

    return yearly, monthly, weekly


def draw_bar_chart(dwg, data, title, width, height, bar_padding=5):
    """Draws a single bar chart into the SVG drawing."""
    if not data:
        return

    # Chart Title
    dwg.add(
        dwg.text(
            title,
            insert=(width / 2, 30),
            text_anchor="middle",
            font_size=20,
            fill="white",
        )
    )

    # Chart Area
    chart_x = 60
    chart_y = 50
    chart_width = width - chart_x - 40
    chart_height = height - chart_y - 50

    max_val = max(data.values()) if data else 1
    slot_width = chart_width / len(data) if data else 0
    max_bar_width = 30  # Max width for a single bar

    # Draw Bars and Labels
    for i, (label, value) in enumerate(data.items()):
        bar_height = (value / max_val) * chart_height

        rect_width = min(slot_width - bar_padding, max_bar_width)
        bar_x = chart_x + i * slot_width + (slot_width - rect_width) / 2
        bar_y = chart_y + chart_height - bar_height

        dwg.add(
            dwg.rect(
                insert=(bar_x, bar_y), size=(rect_width, bar_height), fill="#4DD2FF"
            )
        )

        # Value Label
        dwg.add(
            dwg.text(
                str(value),
                insert=(bar_x + rect_width / 2, bar_y - 5),
                text_anchor="middle",
                font_size=12,
                fill="white",
            )
        )

        # X-axis Label
        label_y = chart_y + chart_height + 20
        text_element = dwg.text(
            str(label),
            insert=(bar_x + rect_width / 2, label_y),
            text_anchor="middle",
            font_size=12,
            fill="white",
        )
        # Rotate weekly labels to prevent overlap
        if len(data) > 20:  # Heuristic for weekly chart
            text_element.rotate(-45, (bar_x + rect_width / 2, label_y))
        dwg.add(text_element)

    # Draw Axes
    dwg.add(
        dwg.line(
            start=(chart_x, chart_y),
            end=(chart_x, chart_y + chart_height),
            stroke="white",
        )
    )
    dwg.add(
        dwg.line(
            start=(chart_x, chart_y + chart_height),
            end=(chart_x + chart_width, chart_y + chart_height),
            stroke="white",
        )
    )


def calculate_streak(activities):
    """Calculates the current push-up streak."""
    if not activities:
        return 0

    dates = sorted(
        list(set(parse(act.start_date).date() for act in activities)), reverse=True
    )

    if not dates:
        return 0

    today = datetime.date.today()
    if dates[0] != today and dates[0] != today - datetime.timedelta(days=1):
        return 0

    streak = 0
    if dates[0] == today:
        streak += 1
        dates.pop(0)

    if not dates:
        return streak

    for i, date in enumerate(dates):
        if i == 0:
            if today - date == datetime.timedelta(days=1):
                streak += 1
            else:
                break
        else:
            if dates[i - 1] - date == datetime.timedelta(days=1):
                streak += 1
            else:
                break

    return streak


def main():
    """Main function to generate the bar chart SVG."""
    activities = get_data()
    if not activities:
        print("No data found in database.")
        return

    yearly_data, monthly_data, weekly_data = process_data(activities)

    streak = calculate_streak(activities)
    print(f"Current streak: {streak} days")

    # --- Generate Yearly Chart ---
    output_yearly = "assets/yearly_chart.svg"
    width, height = 1800, 600
    dwg_yearly = svgwrite.Drawing(output_yearly, profile="full", size=(width, height))
    dwg_yearly.add(dwg_yearly.rect(size=("100%", "100%"), fill="#222222"))
    draw_bar_chart(
        dwg_yearly,
        dict(sorted(yearly_data.items())),
        "Yearly Pushup Totals",
        width,
        height,
    )
    dwg_yearly.save()
    print(f"Yearly chart saved to {output_yearly}")

    # --- Generate Monthly Chart ---
    output_monthly = "assets/monthly_chart.svg"
    dwg_monthly = svgwrite.Drawing(output_monthly, profile="full", size=(width, height))
    dwg_monthly.add(dwg_monthly.rect(size=("100%", "100%"), fill="#222222"))
    draw_bar_chart(
        dwg_monthly,
        dict(sorted(monthly_data.items())),
        "Monthly Pushup Totals",
        width,
        height,
        bar_padding=10,
    )
    dwg_monthly.save()
    print(f"Monthly chart saved to {output_monthly}")

    # --- Generate Weekly Chart ---
    output_weekly = "assets/weekly_chart.svg"
    dwg_weekly = svgwrite.Drawing(output_weekly, profile="full", size=(width, height))
    dwg_weekly.add(dwg_weekly.rect(size=("100%", "100%"), fill="#222222"))
    # Sort and take last 52 weeks for the weekly chart
    sorted_weekly_items = sorted(weekly_data.items())
    draw_bar_chart(
        dwg_weekly,
        dict(sorted_weekly_items[-52:]),
        "Weekly Totals (Last 52 Weeks)",
        width,
        height,
        bar_padding=5,
    )
    dwg_weekly.save()
    print(f"Weekly chart saved to {output_weekly}")


if __name__ == "__main__":
    main()
