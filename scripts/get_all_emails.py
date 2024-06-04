import imap_tools

from sage.config import ENV

"""
Usage:

It's hard to look at the email body from the command line,
it's easier to redirect stdout to a file by adding this like to the command.
> scripts/debug_stdout.txt
"""
RECEIVING_EMAIL_USER = ENV["RECEIVING_EMAIL_USER"]
RECEIVING_EMAIL_PASSWORD = ENV["RECEIVING_EMAIL_PASSWORD"]

count = 0
try:
    print(f"Connecting to mailbox of user {RECEIVING_EMAIL_USER}...")
    with imap_tools.MailBoxUnencrypted("localhost").login(
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
