"""
Tests the email parser (module sage/parsers/email_parser.py) to ensure it
correctly parses an  email into transaction data.

The input is the UID of the email, which maps to an email that was loaded
into the mail server when the docker container was created. These emails
are contained within the file
docker/mailserver/test_data/example_data/txn_emails.mbox

They're also listed as separate files in
tests/test_parsers/test_data/example_data so they can be more easily
viewed.

The expected expected_output is the transaction object defined in
sage/models/transaction.py
"""
import pytest

from sage.mx import get_emails
from sage.parsers import email_parser
from tests import utils
from tests.test_parsers.happy_path_test_cases import TEST_CASES


def get_test_data():
    # Retrieve the email corresponding to the UID
    for test_case in TEST_CASES:
        input = test_case[0]
        uid = input.get("uid")
        emails = get_emails.main(f"uid={uid}")
        for email in emails:
            input["email"] = email
    return TEST_CASES


utils.refresh_inbox("txn_emails.mbox")
DATA = get_test_data()


# TODO: Add test emails for cash transactions
@pytest.mark.parametrize("input,expected_output", DATA)
def test_transaction_bank_parsing(input, expected_output):
    """
    Ensure the right bank was identified. The bank can be
    Huntington, Chase, Discover or cash.
    """
    transaction = email_parser.main(input.get("email"))
    assert expected_output.get("bank") == transaction.bank


@pytest.mark.parametrize("input,expected_output", DATA)
def test_transaction_type_parsing(input, expected_output):
    """
    Ensure that the right transaction type was identified.
    Transaction type can be one of the following

        withdrawal: a merchant removed money from the account

        deposit: a payer added money from the account

        transfer withdrawal: I moved money out of this account to another
        account or I withdrew cash from this account

        transfer deposit: I moved money into this account from another account
        or I deposited cash into this account
    """
    transaction = email_parser.main(input.get("email"))
    assert expected_output.get("type_") == transaction.type_


@pytest.mark.parametrize("input,expected_output", DATA)
def test_transaction_merchant_parsing(input, expected_output):
    """
    If the transaction is a withdrawal, ensure that the right merchant is
    identified. If the transaction is a deposit, ensure that no merchant is
    identified.
    """
    transaction = email_parser.main(input.get("email"))
    assert expected_output.get("merchant") == transaction.merchant


@pytest.mark.parametrize("input,expected_output", DATA)
def test_transaction_payer_parsing(input, expected_output):
    """
    If the transaction is a deposit, ensure that the right payer is
    identified. If the transaction is a withdrawal, ensure that no payer is
    identified.
    """
    transaction = email_parser.main(input.get("email"))
    assert expected_output.get("payer") == transaction.payer


@pytest.mark.parametrize("input,expected_output", DATA)
def test_transaction_amount_parsing(input, expected_output):
    """
    Ensure that the correct amount is identified from the email. Also ensure
    that the format is 00.00
    """
    transaction = email_parser.main(input.get("email"))
    assert expected_output.get("amount") == transaction.amount


@pytest.mark.parametrize("input,expected_output", DATA)
def test_transaction_account_parsing(input, expected_output):
    """
    Ensure that the correct account is identified. The only bank that does not
    have multiple accounts is Chase.
    """
    transaction = email_parser.main(input.get("email"))
    assert expected_output.get("account") == transaction.account


@pytest.mark.parametrize("input,expected_output", DATA)
def test_transaction_balance_parsing(input, expected_output):
    """
    Ensure that the balance was identified. Chase and Discover do not provide
    balance information.
    """
    transaction = email_parser.main(input.get("email"))
    assert expected_output.get("balance") == transaction.balance


@pytest.mark.parametrize("input,expected_output", DATA)
def test_date_parsing(input, expected_output):
    """
    Ensure that the time the alert email was sent to outgoing@gmail.com is
    right. The time the email was forwarded to the mail server should not be
    recorded.
    """
    transaction = email_parser.main(input.get("email"))
    assert expected_output.get("date") == transaction.date
