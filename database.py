import sqlite3
from pathlib import Path

from dotenv import load_dotenv


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
            club_name TEXT NOT NULL,
            distance INTEGER NOT NULL,     
            course_id INTEGER,
            FOREIGN KEY (course_id) REFERENCES courses(id)
            FOREIGN KEY (club_name) REFERENCES bag(id)
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
            SELECT abbreviation, 
                name,
                loft,
                brand
            FROM bag 
            ORDER BY id
            """

        cursor = self.conn.execute(q)

        return [dict(row) for row in cursor]


if __name__ == "__main__":
    load_dotenv()

    db = BagDatabase()
