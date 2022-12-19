# Provides fixtures for the entire directory and subdirectories
# This file is run during the test collection phase (before any tests are run)

import datetime
import os
import pathlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import imap_tools
import pytest
from dotenv import load_dotenv

app_root = str(pathlib.Path(__file__).parent.parent.parent)
env_path = app_root + "/.env"
if not load_dotenv(env_path):
    print(f".env faled to load from {env_path}")
DOMAIN = os.environ.get("DOMAIN")
IMAP4_FQDN = os.environ.get("IMAP4_FQDN")
FORWARDING_EMAIL = os.environ.get("FORWARDING_EMAIL")
RECEIVING_EMAIL_USER = os.environ.get("RECEIVING_EMAIL_USER")
RECEIVING_EMAIL_PASSWORD = os.environ.get("RECEIVING_EMAIL_PASSWORD")


@pytest.fixture()
def send_single_email():
    """
    Send a single pre-defined email to the mail server.
    """

<<<<<<< HEAD
    sender = "root@localhost"
=======
    sender = FORWARDING_EMAIL
>>>>>>> 313c9a058ed2016ebcc3355a24d55e60beaedbf4
    receivers = f"{RECEIVING_EMAIL_USER}@{DOMAIN}"
    now = datetime.datetime.now()

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Sent {now}"
    msg["From"] = sender
    msg["To"] = receivers

    # Create the body of the message
    html = """\
    <html>
    <head></head>
    <body>
        <p>Hi!<br>
        This is a single test email.
        </p>
    </body>
    </html>
    """

    # Record the MIME type
    part1 = MIMEText(html, "html")
    # Attach the part to the message
    msg.attach(part1)

    # For local development:
    #  host = ""
    #  port = 25
    #  local_hostname = localhost
    host = ""
    port = 25
    local_hostname = "localhost"
    smtp_conn = smtplib.SMTP(host, port, local_hostname)

    success = False
    try:
        smtp_conn = smtplib.SMTP("localhost")
        smtp_conn.sendmail(sender, receivers, msg.as_string())
        print("Email successfully sent.")
        success = True
        return success
    except smtplib.SMTPException as error:
        print(f"Error sending email: {error}")
        return success, error


@pytest.fixture()
def get_emails():
    """
    Get emails from the mail server via IMAP
    """
    msgs = []
    with imap_tools.MailBoxUnencrypted(IMAP4_FQDN).login(
        RECEIVING_EMAIL_USER, RECEIVING_EMAIL_PASSWORD
    ) as mailbox:
        for msg in mailbox.fetch():
            email = [
                ("UID", msg.uid),
                ("To:", msg.to),
                ("From:", msg.from_),
                ("Subject:", msg.subject),
                ("HTML", msg.html),
            ]
            msgs.append(email)
    return msgs
