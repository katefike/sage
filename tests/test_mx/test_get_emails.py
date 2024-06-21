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


def test_get_all_emails():
    return


def test_get_forwarded_emails():
    return


def test_get_unparsed_emails():
    return


def test_get_email_by_uid():
    return
