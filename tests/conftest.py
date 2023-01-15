from typing import Dict

import psycopg2
import pytest

from . import ENV


def pytest_configure():
    assert (
        ENV["ISDEV"] == "True"
    ), "CRITICAL: Only run pytest in the development environment."


@pytest.fixture(scope="session")
def env() -> Dict:
    return ENV


@pytest.fixture(scope="session")
def conn():
    try:
        conn = psycopg2.connect(
            host=ENV["POSTGRES_HOST"],
            dbname=ENV["POSTGRES_DB"],
            user=ENV["POSTGRES_USER"],
            password=ENV["POSTGRES_PASSWORD"],
        )
    except psycopg2.DatabaseError as error:
        print(f"Failed to connect to the database: {error}")
        host = ENV["POSTGRES_HOST"]
        db = ENV["POSTGRES_DB"]
        user = ENV["POSTGRES_USER"]
        passw = ENV["POSTGRES_PASSWORD"]
        print(f"HOST: {host} DB: {db} USER: {user} PASS: {passw} ")
    yield conn
    conn.close()


def truncate_tables(conn):
    """Only truncates `public` tables"""

    tables_to_truncate = ["banks"]
    with conn, conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                table_name
            FROM
                information_schema.tables
            WHERE
                table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """
        )
        for result in cursor.fetchall():
            table_name = result[0]
            if table_name in tables_to_truncate:
                continue
            cursor.execute(f"TRUNCATE {table_name} CASCADE")
        print("TRUNCATED TABLES")


@pytest.fixture(scope="function", autouse=True)
def fresh_conn(conn):
    # Preemptive pre-test truncation
    truncate_tables(conn)

    yield conn

    # Post-test truncation
    truncate_tables(conn)
