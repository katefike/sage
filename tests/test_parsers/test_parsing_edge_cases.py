"""
Tests the email parser (module sage/parsers/email_parser.py) to ensure it
can handle exceptions and errors from edge cases.

The input is the UID of the email, which maps to an email that was loaded
into the mail server when the docker container was created. These emails
are contained within the file
docker/mailserver/test_data/example_data/transaction_emails.mbox

They're also listed as separate files in
tests/test_parsers/test_data/example_data so they can be more easily
viewed.

The expected expected_output is the transaction object defined in
sage/models/transaction.py
"""
import pytest

from sage.parsers import email_parser


def test_transaction_bank_parsing():
    """
    Handle error for no date can be parsed from the body.
    """
    body = "---------- Forwarded message ---------"
    "D@te: Mondaaay, Jan 1"
    with pytest.raises(
        email_parser.MatchError, match="Regex failed to get the date from body: {body}"
    ):
        email_parser.get_date(body)
