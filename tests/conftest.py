from typing import Dict

import psycopg2
import pytest

from . import ENV


def pytest_configure():
    assert (
        ENV["ISDEV"] is True
    ), "CRITICAL: Only run pytest in the development environment. \
        ISDEV must be true."


@pytest.fixture(scope="session")
def env() -> Dict:
    return ENV


POSTGRES_HOST = ENV["POSTGRES_HOST"]
POSTGRES_DB = ENV["POSTGRES_DB"]


@pytest.fixture(scope="session")
def admin_db_conn():
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


@pytest.fixture(scope="session")
def etl_db_conn():
    POSTGRES_ETL_USER = "etl"
    POSTGRES_ETL_PASSWORD = ENV["POSTGRES_ETL_PASSWORD"]
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            dbname=POSTGRES_DB,
            user=POSTGRES_ETL_USER,
            password=POSTGRES_ETL_PASSWORD,
        )
    except psycopg2.DatabaseError as error:
        print(f"Failed to connect to the database: {error}")
        print(
            f"HOST: {POSTGRES_HOST} DB: {POSTGRES_DB} USER: {POSTGRES_ETL_USER} \
            PASS: {POSTGRES_ETL_PASSWORD}"
        )
    yield conn
    conn.close()


def truncate_tables(admin_db_conn):
    """Only truncates `public` tables"""

    tables_not_to_truncate = []
    with admin_db_conn, admin_db_conn.cursor() as cursor:
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


def insert_bank_data(admin_db_conn):
    """Insert test bank data into the banks table"""
    with admin_db_conn, admin_db_conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO public.banks (name, account, type, email_addresses, date_opened, date_closed)
            VALUES 
                ('Huntington', 'SAVE', 'liquid', ARRAY['HuntingtonAlerts@email.huntington.com', 'HuntingtonOnline@email.huntington.com'], '2024-01-01', '2024-12-31'),
                ('Huntington', 'CHECK', 'liquid', ARRAY['HuntingtonAlerts@email.huntington.com', 'HuntingtonOnline@email.huntington.com'], '2024-01-01', '2024-12-31'),
                ('Huntington', 'CK9706', 'liquid', ARRAY['HuntingtonAlerts@email.huntington.com', 'HuntingtonOnline@email.huntington.com'], '2024-01-01', '2024-12-31'),
                ('Discover', 'student', 'credit', ARRAY['discover@services.discover.com'], '2024-01-01', '2024-12-31'),
                ('Discover', 'miles', 'credit', ARRAY['discover@services.discover.com'], '2024-01-01', '2024-12-31'),
                ('Discover', 'savings', 'liquid', ARRAY['discover@services.discover.com'], '2024-01-01', '2024-12-31')
        """)
        cursor.execute("""
            INSERT INTO public.banks (name, type, email_addresses, date_opened, date_closed)
            VALUES ('Chase', 'credit', ARRAY['no.reply.alerts@chase.com'], '2024-01-01', '2024-12-31')
        """)
        
        print("INSERTED BANK DATA")


@pytest.fixture(scope="function", autouse=True)
def fresh_conn(admin_db_conn, etl_db_conn):
    # Preemptive pre-test truncation
    truncate_tables(admin_db_conn)
    
    # Insert bank data for tests
    insert_bank_data(admin_db_conn)

    yield etl_db_conn

    # Post-test truncation
    truncate_tables(admin_db_conn)
