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

The expected expected_output is the Transaction object defined in
sage/models/transaction.py
"""
import pytest
import imap_tools

from sage.db import emails
from sage.mx import get_emails
from sage.parsers import email_parser
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


def test_get_bank_config_emails():
    """
    Load an mbox containing emails from banks.email_addresses in the DB.
    """
    banks_email_addresses = get_emails.get_banks_config_email_addresses()

    utils.refresh_inbox("bank_config_example_emails.mbox")
    all_emails = get_emails.main("forwarded")
    assert len(all_emails) == len(banks_email_addresses)


def test_get_unparsed_emails():
    """
    Insert data into the emails table, simulating initially unparsed
    emails. Load parsable emails. Run sage and verify they were all
    processed.
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


def test_get_manual_forward_origin_error():
    """
    Raise error when Subject starts with Fwd:
    but body does not contain From:
    """
    msg = imap_tools.MailMessage
    msg.uid = 1
    msg.subject = " Fwd: Test"
    body = "Invalid"

    with pytest.raises(
        email_parser.RegexError,
        match=f"Failed to parse origin from manually forwarded email with UID {msg.uid}"""
    ):
        get_emails.get_manual_forward_origin(msg, body)
