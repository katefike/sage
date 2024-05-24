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
import re

import pytest

from sage.parsers import email_parser


def test_get_date_regex_error():
    """
    Handle error for no date parsed from a body.
    """
    body = "---------- Forwarded message ---------"
    "D@te: Mondaaay, Jan 1"
    with pytest.raises(
        email_parser.RegexError, match=f"Regex failed to get the date from body"
    ):
        email_parser.get_date(body)


def test_parse_chase_merchant_regex_error():
    """
    Handle error for no merchant parsed from a Chase transaction email
    subject.
    """
    subject = "Your $100 transaction con MI COMERCIANTE"
    with pytest.raises(
        email_parser.RegexError,
        match="Regex failed to get the merchant from a Chase email subject",
    ):
        email_parser.parse_chase(subject)


def test_parse_chase_raw_amount_regex_error():
    """
    Handle error for no raw amount parsed from a Chase transaction email
    subject.
    """
    subject = "Your $1oo.oo transacción with MI COMERCIANTE"
    with pytest.raises(
        email_parser.RegexError,
        match="Regex failed to get the raw amount from a Chase email subject",
    ):
        email_parser.parse_chase(subject)


def test_parse_discover_merchant_regex_error():
    """
    Handle error for no merchant parsed from a Discover transaction
    email body.
    """
    body = """
    Comerciante: foop
    Amount: $23.50
    """
    with pytest.raises(
        email_parser.RegexError,
        match="Regex failed to get the merchant from a Discover email body",
    ):
        email_parser.parse_discover(body)


def test_parse_discover_raw_amount_regex_error():
    """
    Handle error for no raw amount parsed from a Discover transaction
    email body.
    """
    body = """
    Merchant: SQ *EARTH BISTRO CAFE
    Amount: bloop
    """
    with pytest.raises(
        email_parser.RegexError,
        match="Regex failed to get the raw amount from a Discover email body",
    ):
        email_parser.parse_discover(body)


def test_parse_huntington_transfer_withdrawal_regex_error():
    """
    Handle error for no raw amount parsed from a Huntington
    transfer withdrawal transaction email body.
    """
    body = "We've been posessed by a toad!"
    with pytest.raises(
        email_parser.RegexError,
        match="Regex failed to get the raw amount from a Huntington transfer withdrawal email body",
    ):
        email_parser.parse_huntington_transfer_withdrawal(body)
