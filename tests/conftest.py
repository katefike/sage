import os
import pathlib

import pytest
from dotenv import load_dotenv


def pytest_configure():
    app_root = str(pathlib.Path(__file__).parent.parent)
    env_path = app_root + "/.env"
    if not load_dotenv(env_path):
        print(f".env faled to load from {env_path} via the dotenv loader.")
    pytest.DOMAIN = os.environ.get("DOMAIN")
    pytest.IMAP4_FQDN = os.environ.get("IMAP4_FQDN")
    pytest.FORWARDING_EMAIL = os.environ.get("FORWARDING_EMAIL")
    pytest.RECEIVING_EMAIL_USER = os.environ.get("RECEIVING_EMAIL_USER")
    pytest.RECEIVING_EMAIL_PASSWORD = os.environ.get(
        "RECEIVING_EMAIL_PASSWORD"
    )  # noqa: E501,E261,W292

def truncate_db(db_conn):
    """Only truncates `public` tables"""

    LIST_OF_TABLES_NOT_TO_TRUNCATE = []
    with db_conn, db_conn.cursor() as cursor:
        cursor.execute(
            """
SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_type = 'BASE TABLE'
            """
        )
        for result in cursor.fetchall():
            table_name = result[0]
            if table_name in LIST_OF_TABLES_NOT_TO_TRUNCATE:
                # we don't want these truncated
                continue
            cursor.execute(f"TRUNCATE {table_name} CASCADE")

        cursor.execute(
            """
TRUNCATE auth.audit_log_entries
            """
        )

        # cleanup users
        cursor.execute(
            """
DELETE FROM auth.users
            """
        )

        print("TRUNCATED DB")


