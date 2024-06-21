"""
Tests the entrypoint of the program, __main__.py
"""
from sage.__main__ import main
from sage.db import emails
from sage.models.email import Email
from sage.mx import get_emails

from . import ENV, utils


def test_unretrieved_email():
    """
    Send an email that isn't from the forwarding email.
    It should not be retrieved from the inbox.
    """
    utils.delete_inbox_emails()
    html_body = """\
    <html>
    <head></head>
    <body>
        <p>Hi!<br>
        This is a single test email.
        </p>
    </body>
    </html>
    """
    sender = "test.unretrieved.email@aol.com"
    utils.send_email(html_body, sender)
    msg_count = main()
    assert msg_count.get("retrieved") == 0


def test_unparsable_emails():
    """
    Load unparasble emails. They are from the forwarding email but are not
    txns. They should be retrieved from the inbox and left unparsed.
    """

    utils.refresh_inbox("unparsable_emails.mbox")
    msg_count = main()
    assert msg_count.get("retrieved") == msg_count.get("unparsed")


def test_retry_unparsed_emails():
    """
    Insert data into the emails table, simulating initially unparsed emails.
    Load parsable emails. Run sage and verify they were all processed.
    """
    utils.refresh_inbox("transaction_emails.mbox")
    emails_ = get_emails.main(filter="forwarded")
    # Retrieve all emails in the inbox from the forwarding email
    for email in emails_:
        emails.insert_email(email)

    email_count = main(retry_unparsed_emails=True)
    assert len(emails_) == email_count.get("retrieved")
    assert email_count.get("retrieved") == email_count.get("processed")
    breakpoint()
