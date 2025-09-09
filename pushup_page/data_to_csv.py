import sqlite3
import csv

from pushup_page.config import SQL_FILE


def main():
    data = sqlite3.connect(SQL_FILE)
    cursor = data.cursor()
    cursor.execute("SELECT * FROM activities")
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()

    with open("pushup_data.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        writer.writerows(rows)


if __name__ == "__main__":
    main()
