import sys
import os
import sqlite3
import csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pushup_page.config import SQL_FILE


def main():
    data = sqlite3.connect(SQL_FILE)
    cursor = data.cursor()
    cursor.execute("SELECT * FROM activities")
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()

    def apply_duration_time(d):
        try:
            return d.split()[1].split(".")[0]
        except Exception as e:
            print(f"Error applying duration time: {e}")
            return ""

    with open("pushup_data.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        for row in rows:
            row = list(row)
            if "elapsed_time" in columns:
                elapsed_time_index = columns.index("elapsed_time")
                row[elapsed_time_index] = apply_duration_time(row[elapsed_time_index])
            writer.writerow(row)


if __name__ == "__main__":
    main()
