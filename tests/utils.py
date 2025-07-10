import datetime
import smtplib
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

import imap_tools

from sage.db import emails
from sage.models.email import Email

from . import ENV, BANKS_CONFIG


def refresh_inbox(mbox_name: str):
    """
    Re-create the user's Maildir. Then reads a directory
    containing an mbox format mailbox and creates a Maildir format mailbox.

    The command doveadm expunge -u {EN['RECEIVING_EMAIL_USER']} mailbox 'INBOX' all
    is insufficient because it does not restart incrementing of the UIDs
    at 1.
    """
    print(f"Refreshing inbox with mbox {mbox_name}...")

    container = "docker exec sage-mx"
    maildir_path = f"/home/{ENV['RECEIVING_EMAIL_USER']}/Maildir/"
    # The mbox path MUST be the full file path
    # Otherwise fails with error "Fatal: Source is not an mbox file or a directory!"
    # https://www.linuxquestions.org/questions/linux-server-73/mb2md-problem-891502/
    mbox_path = "./test_data/example_data"

    print("Recreating Maildir/...")
    subprocess.call(
        f"{container} rm -r {maildir_path} && mkdir {maildir_path}",
        shell=True,
    )
    print("Loading mbox into Maildir/...")
    subprocess.call(
        f"{container} mb2md -s {mbox_path}/{mbox_name} -d {maildir_path}",
        shell=True,
    )
    print("modifying Maildir/ permissions...")
    subprocess.call(
        f"{container} chmod -R 777 {maildir_path}",
        shell=True,
    )


def get_inbox_emails(input_uid: Optional[int] = None) -> List:
    msgs = []
    try:
        with imap_tools.MailBoxUnencrypted("localhost").login(
            ENV["RECEIVING_EMAIL_USER"], ENV["RECEIVING_EMAIL_PASSWORD"]
        ) as mailbox:
            if input_uid:
                for msg in mailbox.fetch(imap_tools.AND(uid=[input_uid])):
                    msgs.append(msg)
            else:
                for msg in mailbox.fetch():
                    msgs.append(msg)
        return msgs
    except imap_tools.MailboxLoginError as error:
        print(f"CRITICAL: Failed to login to the mailbox: {error}")


def delete_inbox_emails():
    container = "docker exec sage-mx"
    try:
        subprocess.call(
            f"{container} doveadm expunge -u {ENV['RECEIVING_EMAIL_USER']} mailbox 'INBOX' all",
            shell=True,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
    except subprocess.CalledProcessError as error:
        print(f"CRITICAL: Failed to delete emails: {error.returncode}: {error.output}")
    msgs = get_inbox_emails()
    email_count = len(msgs)
    if email_count == 0:
        print("Successfully deleted all emails in the inbox.")
    else:
        print(f"CRITICAL: Failed to delete emails, {email_count} emails were counted.")


def send_email(html_body: Optional[str] = None, sender: Optional[str] = None) -> bool:
    """
    Send a single pre-defined email to the mail server.
    """
    if not sender:
        sender = ENV["FORWARDING_EMAIL"]

    receivers = f"{ENV['RECEIVING_EMAIL_USER']}@{ENV['DOMAIN']}"
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
        return True
    except smtplib.SMTPException as error:
        print(f"Error sending email: {error}")
        return False


def insert_db_email(email: Optional[Email] = None) -> int:
    if not email:
        email = Email(
            uid=1,
            batch_time="2023-08-31 15:22:40",
            forwarded_date="2023-08-31",
            manually_forwarded=True,
            from_="bank@localhost",
            subject="Example Transaction Email",
            html="f",
            body="Hello world!",
        )
    email_id = emails.insert_email(email)
    return email_id
