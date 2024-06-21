"""
Tests getting emails (module sage/mx/get_emails.py).

There are four filters:
    1. Get all emails
    2. Get emails forwarded by the email associated with
        the env var `FORWARDING_EMAIL`.
    3. Get all emails in the DB table emails that the parser already attempted
        to parse and didn't ifentify a txn.
    4. Get email by UID.

They're also listed as separate files in
tests/test_parsers/test_data/example_data so they can be more easily
viewed.

The expected expected_output is the transaction object defined in
sage/models/transaction.py
"""

from sage.db import emails
from sage.mx import get_emails
from tests import utils


def test_get_all_emails():
    """
    Load an mbox containing two emails from the forwarding email.
    And send an email from a random email address. All 3 emails should be
    retrieved.
    """
    utils.refresh_inbox("identical_txns_gmail+cloudHQ_forwards.mbox")

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
    sender = "random_email@aol.com"
    utils.send_email(html_body, sender)

    all_emails = get_emails.main()
    assert len(all_emails) == 3


def test_get_forwarded_emails():
    utils.refresh_inbox("identical_txns_gmail+cloudHQ_forwards.mbox")
    all_emails = get_emails.main("forwarded")
    assert len(all_emails) == 2


def test_get_unparsed_emails():
    """
    Insert data into the emails table, simulating initially unparsed emails.
    Load parsable emails. Run sage and verify they were all processed.
    """
    utils.refresh_inbox("identical_txns_gmail+cloudHQ_forwards.mbox")
    emails_ = get_emails.main(filter="forwarded")
    for email in emails_:
        emails.insert_email(email)

    unparsed_emails = get_emails.main(filter="unparsed")
    assert len(unparsed_emails) == 2


def test_get_email_by_uid():
    utils.refresh_inbox("identical_txns_gmail+cloudHQ_forwards.mbox")
    emails_ = get_emails.main(filter="uid=1")
    assert len(emails_) == 1
    for email in emails_:
        assert email.uid == 1
