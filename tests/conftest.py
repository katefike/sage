import datetime
import smtplib
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Optional

import imap_tools
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


@pytest.fixture
def send_email(env: Dict):
    def _send_email(html_body: str, sender: Optional[str] = None):
        """
        Send a single pre-defined email to the mail server.
        """
        if not sender:
            sender = env.get("FORWARDING_EMAIL")

        receivers = f"{env.get('RECEIVING_EMAIL_USER')}@{env.get('DOMAIN')}"
        now = datetime.datetime.now()

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Sent {now}"
        msg["From"] = sender
        msg["To"] = receivers

        # Record the MIME type
        part1 = MIMEText(html_body, "html")
        # Attach the part to the message
        msg.attach(part1)

        # host = ""
        # port = 25
        # local_hostname = "localhost"
        # smtp_conn = smtplib.SMTP(host, port, local_hostname)

        try:
            smtp_conn = smtplib.SMTP("localhost")
            smtp_conn.sendmail(sender, receivers, msg.as_string())
            print("Email successfully sent.")
            success = True
            return success
        except smtplib.SMTPException as error:
            print(f"Error sending email: {error}")
            return

    return _send_email


@pytest.fixture()
def total_emails(env: Dict):
    """
    Get all emails from the mail server via IMAP
    """
    msgs = []
    with imap_tools.MailBoxUnencrypted(env.get("IMAP4_FQDN")).login(
        env.get("RECEIVING_EMAIL_USER"), env.get("RECEIVING_EMAIL_PASSWORD")
    ) as mailbox:
        for msg in mailbox.fetch():
            msgs.append(msg)
    return msgs


@pytest.fixture(scope="function")
def delete_all_emails(env: Dict):
    """Delete all emails for the receiving email's inbox"""
    try:
        subprocess.call(
            f"docker exec sage-mailserver-1 doveadm expunge -u {env['RECEIVING_EMAIL_USER']} mailbox 'INBOX' all",
            shell=True,
        )
    except Exception as error:
        print(
            f"CRITICAL: Failed to delete all emails from the mailserver container: {error}"
        )
