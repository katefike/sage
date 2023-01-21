import datetime
import smtplib
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import imap_tools

from . import ENV


def fresh_inbox(mbox_name: str):
    """
    Re-create the user's Maildir. Then reads a directory
    containing an Mbox format mailbox and creates a Maildir format mailbox.

    The command doveadm expunge -u {EN['RECEIVING_EMAIL_USER']} mailbox 'INBOX' all
    is insufficient because it does not restart incrementing of the UIDs
    at 1.
    """
    container = "docker exec sage-mailserver-1"
    maildir_path = f"/home/{ENV['RECEIVING_EMAIL_USER']}/Maildir/"
    mbox_path = f"/home/{ENV['RECEIVING_EMAIL_USER']}/test_data/example_data"
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
        print("Successfully loaded emails from mbox file.")
    except Exception as error:
        print(f"CRITICAL: Failed to create an inbox from an mbox: {error}")


def delete_emails():
    try:
        container = "docker exec sage-mailserver-1"
        subprocess.call(
            f"{container} doveadm expunge -u {ENV['RECEIVING_EMAIL_USER']} mailbox 'INBOX' all",
            shell=True,
        )
        print("Successfully deleted all emails in the inbox.")
    except Exception as error:
        print(f"CRITICAL: Failed to delete emails: {error}")


def get_mailbox():
    with imap_tools.MailBoxUnencrypted(ENV["IMAP4_FQDN"]).login(
        ENV["RECEIVING_EMAIL_USER"], ENV["RECEIVING_EMAIL_PASSWORD"]
    ) as mailbox:
        return mailbox


def send_email():
    def _send_email(html_body: Optional[str] = None, sender: Optional[str] = None):
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
            success = True
            return success
        except smtplib.SMTPException as error:
            print(f"Error sending email: {error}")
            return

    return _send_email


def email_count():
    """
    Get all emails from the mail server via IMAP
    """
    msgs = []
    mailbox = get_mailbox()
    for msg in mailbox.fetch():
        msgs.append(msg)
    return msgs
