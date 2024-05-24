"""
Tests the email parser (module sage/parsers/email_parser.py) to ensure it
can handle exceptions and errors from regex edge cases.

The input is the transaction email bod. It's a big string containing the forwarded email.
I. e.
--00000000000010b66806191115a5
Content-Type: text/plain; charset="UTF-8"
Content-Transfer-Encoding: quoted-printable

Forwarded using cloudHQ's free email forwarding tool: Multi Email Forward
For Gmail <https://www.multi-email-forward.com/>
You might be also interested to try cloudHQ's Google Forms Templates
<https://www.google-forms-templates.com>: *Professional and Free Google
Forms templates*

---------- Forwarded message ---------
From: Huntington Alerts <HuntingtonAlerts@email.huntington.com>
Date: Mon, 13 May 2024 03:15:40 -0600
Subject: Withdrawal or Purchase
To: outgoing@gmail.com
Date Sent: Mon, 13 May 2024 03:15:40 -0600
Date Received: Mon, 13 May 2024 02:15:46 -0700 (PDT)

We've processed a withdrawal or purchase above the amount you set for an
alert.


Hello,

Just a heads up for you. We've processed an ACH withdrawal for $50.00 at
VENMO PAYMENT from your account nicknamed CHECK. That's above the $0.00 you
set for an alert.

Your balance is $866.27 as of 5/13/24 4:30 AM ET.

Thank you for banking with Huntington.

You received this message because you turned on email alerts for certain
events or conditions related to your Huntington account(s). 

This email was generated automatically. Please do not reply to this message

--00000000000010b66806191115a5--

The expected expected_output is the transaction object defined in
sage/models/transaction.py
"""
import pytest

from sage.parsers import email_parser


def test_get_date_regex_error():
    """
    Raise error when no date parsed from a body.
    """
    body = "Invalid"
    with pytest.raises(
        email_parser.RegexError, match=f"Regex failed to get the date from body"
    ):
        email_parser.get_date(body)


def test_parse_huntington_transfer_withdrawal_regex_error():
    """
    Raise error when no raw amount parsed from a Huntington
    transfer withdrawal transaction email body.
    """
    body = "Invalid"
    with pytest.raises(
        email_parser.RegexError,
        match="Regex failed to get the raw amount from a Huntington transfer withdrawal email body",
    ):
        email_parser.parse_huntington_transfer_withdrawal(body)


def test_parse_huntington_transfer_deposit_regex_error():
    """
    Raise error when no raw amount parsed from a Huntington
    transfer deposit transaction email body.
    """
    body = "Invalid"
    with pytest.raises(
        email_parser.RegexError,
        match="Regex failed to get the raw amount from a Huntington transfer deposit email body",
    ):
        email_parser.parse_huntington_transfer_deposit(body)


def test_parse_huntington_withdrawal_merchant_regex_error():
    """
    Raise error when no merchant parsed from a Huntington
    withdrawal transaction email body.
    """
    body = """
    We've processed an ACH withdrawal for $10,000.00 at INVALID MERCHANT from yo acct nicknamed SAVE.
    """
    with pytest.raises(
        email_parser.RegexError,
        match="Regex failed to get the merchant from a Huntington withdrawal email body",
    ):
        email_parser.parse_huntington_withdrawal(body)


def test_parse_huntington_deposit_raw_amount_regex_error():
    """
    Raise error when no raw amount parsed from a Huntington
    deposit transaction email body.
    """
    body = """
    We've processed an ACH deposit for foop at TREASURY DIRECT TREAS DRCT from your account nicknamed SAVE.
    """
    with pytest.raises(
        email_parser.RegexError,
        match="Regex failed to get the raw amount from a Huntington deposit email body",
    ):
        email_parser.parse_huntington_deposit(body)


def test_parse_huntington_deposit_payer_regex_error():
    """
    Raise error when no payer parsed from a Huntington
    deposit transaction email body.
    """
    body = """
    We've processed an ACH deposit for $59.81 from INVALID to yo acct nicknamed CHECK.
    """
    with pytest.raises(
        email_parser.RegexError,
        match="Regex failed to get the payer from a Huntington deposit email body",
    ):
        email_parser.parse_huntington_deposit(body)


def test_get_huntington_account_regex_error():
    """
    Raise error when no account parsed from a Huntington
    transaction email body.
    """
    body = "Invalid"
    with pytest.raises(
        email_parser.RegexError,
        match="Regex failed to get the account from a Huntington transaction email body",
    ):
        email_parser.get_huntington_account(body)


def test_get_huntington_balance_regex_error():
    """
    Raise error when no balance parsed from a Huntington
    transaction email body.
    """
    body = "Invalid"
    with pytest.raises(
        email_parser.RegexError,
        match="Regex failed to get the balance from a Huntington transaction email body",
    ):
        email_parser.get_huntington_balance(body)
