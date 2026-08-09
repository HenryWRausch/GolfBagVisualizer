import sqlite3
from datetime import date
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv


class Filter(TypedDict, total=False):
    # holds the details that we want to include in a given plot
    # TODO - figure out whether we want to allow specific dates
    course_ids: list[int]
    date_range: tuple[date, date]  # start, end
    clubs: list[int]


class BagDatabase:
    # Handle creation and management of a given player's bag

    def __init__(self, player_name: str = "Demo"):
        # includes a demo user by default, we'll ship with a demo.bag to show some base features

        # configure a players name and construct the path to their file
        self.player_name = player_name
        self.db_loc = Path("players") / (player_name + ".db")

        self.conn = sqlite3.connect(self.db_loc)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        # We trust that we are the only ones touching .bag files,
        # so we trust that if a table exists it's correct

        tables = (
            """CREATE TABLE IF NOT EXISTS bag (
            id INTEGER PRIMARY KEY,
            abbreviation TEXT,
            name TEXT NOT NULL,
            loft REAL NOT NULL,
            brand TEXT NOT NULL,
            UNIQUE(name, loft, brand)
            );""",
            """CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
            );""",
            """CREATE TABLE IF NOT EXISTS shots (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            club_id TEXT NOT NULL,
            distance INTEGER NOT NULL,     
            course_id INTEGER,
            FOREIGN KEY (course_id) REFERENCES courses(id)
            FOREIGN KEY (club_id) REFERENCES bag(id)
            );""",
        )

        for table in tables:
            self.conn.execute(table)

        self.conn.commit()

    def get_bag(self):
        # return a list of dictionaries containing all clubs in the player's bag
        # for now returns in id order
        # TODO - eventually needs to return in order of distance

        q = """
            SELECT id,
                abbreviation, 
                name,
                loft,
                brand
            FROM bag 
            ORDER BY id
            """

        cursor = self.conn.execute(q)

        return [dict(row) for row in cursor]

    def get_shots(self, filter_: Filter | None = None):
        # this does not handle order, we'll address that when organizing for graphing
        q = """
            SELECT date,
                club_id, 
                course_id,
                distance
            FROM shots
            WHERE 1 = 1
            """
        if filter_ is None:
            filter_ = Filter()

        params: list[date | int] = []

        if "course_ids" in filter_:
            courses = filter_["course_ids"]
            if len(courses) > 0:
                q += " AND course_id in (" + ",".join(["?"] * len(courses)) + ")"
                params.extend(courses)

        if "date_range" in filter_:
            q += " AND date BETWEEN ? AND ?"
            params.extend(filter_["date_range"])

        if "clubs" in filter_:
            clubs = filter_["clubs"]
            if len(clubs) > 0:
                q += " AND club_id in (" + ",".join(["?"] * len(clubs)) + ")"
                params.extend(clubs)

        cursor = self.conn.execute(q, tuple(params))

        return [dict(i) for i in cursor.fetchall()]


if __name__ == "__main__":
    load_dotenv()

    db = BagDatabase()
    sample_filter = Filter()

    db.get_shots(
        {
            "clubs": [1, 2, 3],
            "course_ids": [1, 2],
            "date_range": (date(2026, 1, 11), date(2026, 3, 14)),
        }
    )
