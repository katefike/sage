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
def fresh_inbox(env: Dict):
    def _fresh_inbox(mbox_name: str):
        """
        Re-create the user's Maildir. Then reads a directory
        containing an Mbox format mailbox and creates a Maildir format mailbox.

        The command doveadm expunge -u {env['RECEIVING_EMAIL_USER']} mailbox 'INBOX' all
        is insufficient because it does not restart incrementing of the UIDs
        at 1.
        """
        container = "docker exec sage-mailserver-1"
        maildir_path = f"/home/{env['RECEIVING_EMAIL_USER']}/Maildir/"
        mbox_path = f"/home/{env['RECEIVING_EMAIL_USER']}/test_data/example_data"
        try:
            subprocess.call(
                f"{container} rm -r {maildir_path} && mkdir {maildir_path}",
                shell=True,
            )
            print("Recreated Maildir/.")
            subprocess.call(
                f"{container} mb2md -s {mbox_path}/{mbox_name} -d {maildir_path}",
                shell=True,
            )
            subprocess.call(
                f"{container} chmod -R 777 {maildir_path}",
                shell=True,
            )
            print(f"{container} chmod -R 777 {maildir_path}")
            print("Successfully loaded emails from mbox file.")
        except Exception as error:
            print(f"CRITICAL: Failed to create an inbox from an mbox: {error}")

    return _fresh_inbox


@pytest.fixture
def send_email(env: Dict):
    def _send_email(html_body: Optional[str] = None, sender: Optional[str] = None):
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

        if html_body:
            # Record the MIME type
            part1 = MIMEText(html_body, "html")
            # Attach the part to the message
            msg.attach(part1)

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


@pytest.fixture
def delete_emails(env: Dict):
    try:
        container = "docker exec sage-mailserver-1"
        subprocess.call(
            f"{container} doveadm expunge -u {env['RECEIVING_EMAIL_USER']} mailbox 'INBOX' all",
            shell=True,
        )
        print("Successfully deleted all emails in the inbox.")
    except Exception as error:
        print(f"CRITICAL: Failed to delete emails: {error}")


@pytest.fixture()
def email_count(env: Dict):
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
