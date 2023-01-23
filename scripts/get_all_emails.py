import os
import pathlib
import sys

import imap_tools
from dotenv import load_dotenv

"""
Usage:

It's hard to look at the email body from the command line,
it's easier to redirect stdout to a file by adding this like to the command.
> scripts/debug_stdout.txt
"""
# Get all environment variables
app_root = str(pathlib.Path(__file__).parent.parent)
env_path = app_root + "/.env"
if not load_dotenv(env_path):
    print(f"ENVIRONMENT ERROR: .env failed to load from {env_path}")
IMAP4_FQDN = os.environ.get("IMAP4_FQDN")
FORWARDING_EMAIL = os.environ.get("FORWARDING_EMAIL")
RECEIVING_EMAIL_USER = os.environ.get("RECEIVING_EMAIL_USER")
RECEIVING_EMAIL_PASSWORD = os.environ.get("RECEIVING_EMAIL_PASSWORD")

count = 0
try:
    with imap_tools.MailBoxUnencrypted(IMAP4_FQDN).login(
        RECEIVING_EMAIL_USER, RECEIVING_EMAIL_PASSWORD
    ) as mailbox:
        for msg in mailbox.fetch():
            count = count + 1
            print(f"UID: {msg.uid}")
            print(f"Date: {msg.date}")
            print(f"To: {msg.to}")
            print(f"From: {msg.from_}")
            if msg.text:
                print(f"Text: {msg.text}")
            else:
                print(f"HTML: {msg.html}")
        print(f"{count} emails were retrieved.")
except imap_tools.MailboxLoginError as error:
    print("FAILED")
    print(
        f"MAILSERVER ERROR: Failed to connect via IMAP to the inbox of user {RECEIVING_EMAIL_USER}: {error}"
    )
