from typing import Dict

import psycopg2
import pytest

from . import ENV


def pytest_configure():
    assert (
        ENV["ISDEV"] is True
    ), "CRITICAL: Only run pytest in the development environment."


@pytest.fixture(scope="session")
def env() -> Dict:
    return ENV


@pytest.fixture(scope="session")
def conn():
    POSTGRES_HOST = ENV["POSTGRES_HOST"]
    POSTGRES_DB = ENV["POSTGRES_DB"]
    POSTGRES_USER = ENV["POSTGRES_USER"]
    POSTGRES_PASSWORD = ENV["POSTGRES_PASSWORD"]
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )
    except psycopg2.DatabaseError as error:
        print(f"Failed to connect to the database: {error}")
        print(
            f"HOST: {POSTGRES_HOST} DB: {POSTGRES_DB} USER: {POSTGRES_USER} \
            PASS: {POSTGRES_PASSWORD}"
        )
    yield conn
    conn.close()


def truncate_tables(conn):
    """Only truncates `public` tables"""

    tables_not_to_truncate = ["banks"]
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
            if table_name in tables_not_to_truncate:
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
