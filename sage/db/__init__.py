import pathlib
import sqlite3

DB_PATH = pathlib.Path(__file__).parent.parent.parent / "sage_db.db"


def open_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def open_cursor():
    cursor = open_connection().cursor()
    return cursor
