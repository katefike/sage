# Provides fixtures for the entire directory and subdirectories
# This file is run during the test collection phase (before any tests are run)

import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import imap_tools
import pytest


@pytest.fixture()
def send_single_email():
    """
    Send a single pre-defined email to the mail server.
    """

    sender = pytest.FORWARDING_EMAIL
    receivers = f"{pytest.RECEIVING_EMAIL_USER}@{pytest.DOMAIN}"
    now = datetime.datetime.now()

    # Create message container - the correct MIME type is 
    # multipart/alternative.
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
def get_all_emails():
    """
    Get all emails from the mail server via IMAP
    """
    msgs = []
    with imap_tools.MailBoxUnencrypted(pytest.IMAP4_FQDN).login(
        pytest.RECEIVING_EMAIL_USER, pytest.RECEIVING_EMAIL_PASSWORD
    ) as mailbox:
        for msg in mailbox.fetch():
            msgs.append(msg)
    return msgs
