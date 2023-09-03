"""
Tests the email parser (module sage/parsers/email_parser.py) to ensure it
correctly parses an  email into transaction data.

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
from tests import utils


def get_test_data():
    data = [
        (
            (dict(uid="3", email_id=1)),
            (
                dict(
                    date="2022-10-06",
                    type_="transfer withdrawal",
                    bank="Huntington",
                    merchant=None,
                    payer=None,
                    amount="999.51",
                    account="checking",
                    balance="1693.13",
                )
            ),
        ),
        (
            (dict(uid="14", email_id=2)),
            (
                dict(
                    date="2022-10-06",
                    type_="transfer deposit",
                    bank="Huntington",
                    merchant=None,
                    payer=None,
                    amount="999.51",
                    account="savings",
                    balance="20000.00",
                )
            ),
        ),
        (
            (dict(uid="5", email_id=3)),
            (
                dict(
                    date="2022-09-13",
                    type_="withdrawal",
                    bank="Huntington",
                    merchant="VENMO PAYMENT",
                    payer=None,
                    amount="200.00",
                    account="checking",
                    balance="14.80",
                )
            ),
        ),
        (
            (dict(uid="7", email_id=4)),
            (
                dict(
                    date="2022-08-08",
                    type_="withdrawal",
                    bank="Huntington",
                    merchant="TREASURY DIRECT TREAS DRCT",
                    payer=None,
                    amount="10000.00",
                    account="savings",
                    balance="14000.00",
                )
            ),
        ),
        (
            (dict(uid="9", email_id=5)),
            (
                dict(
                    date="2022-10-06",
                    type_="withdrawal",
                    bank="Chase",
                    merchant="EB *TRAUMA 2022",
                    payer=None,
                    amount="113.11",
                    account=None,
                    balance=None,
                )
            ),
        ),
        (
            (dict(uid="11", email_id=6)),
            (
                dict(
                    date="2022-08-24",
                    type_="transfer withdrawal",
                    bank="Huntington",
                    merchant=None,
                    payer=None,
                    amount="500.00",
                    account="savings",
                    balance="16000.00",
                )
            ),
        ),
        (
            (dict(uid="17", email_id=7)),
            (
                dict(
                    date="2022-10-05",
                    type_="withdrawal",
                    bank="Discover",
                    merchant="BOMBAY SITAR",
                    payer=None,
                    amount="20.18",
                    account=None,
                    balance=None,
                )
            ),
        ),
        (
            (dict(uid="19", email_id=8)),
            (
                dict(
                    date="2022-08-24",
                    type_="transfer deposit",
                    bank="Huntington",
                    merchant=None,
                    payer=None,
                    amount="500.00",
                    account="checking",
                    balance="757.06",
                )
            ),
        ),
        (
            (dict(uid="21", email_id=9)),
            (
                dict(
                    date="2022-08-24",
                    type_="deposit",
                    bank="Huntington",
                    merchant=None,
                    payer="CHASE CREDIT CRD RWRD RDM",
                    amount="17.09",
                    account="checking",
                    balance="257.06",
                )
            ),
        ),
    ]

    # Retrieve the email corresponding to the UID
    for email in data:
        input = email[0]
        uid = input.get("uid")
        msgs = utils.get_inbox_euidut_uid)
        if len(msgs) == 0:
            print(f"CRITICAL: No email having UID {uid} was found.")
        if len(msgs) > 1:
            print(f"CRITICAL: More than one email having UID {uid} was found.")
        # Iterate over messages,
        # but we're only expecting a single email message in the object.
        for msg in msgs:
            input["msg"] = msg

        input["email_id"] = input.get("email_id")

    return data


utils.fresh_inbox("transaction_emails.mbox")
DATA = get_test_data()


# TODO: Add test emails for cash transactions
@pytest.mark.parametrize("input,expected_output", DATA)
def test_transaction_bank_parsing(input, expected_output):
    """
    Ensure the right bank was identified. The bank can be
    Huntington, Chase, Discover or cash.
    """
    transaction = email_parser.main(input.get("msg"), input.get("email_id"))
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
    transaction = email_parser.main(input.get("msg"), input.get("email_id"))
    assert expected_output.get("type_") == transaction.type_


@pytest.mark.parametrize("input,expected_output", DATA)
def test_transaction_merchant_parsing(input, expected_output):
    """
    If the transaction is a withdrawal, ensure that the right merchant is
    identified. If the transaction is a deposit, ensure that no merchant is
    identified.
    """
    transaction = email_parser.main(input.get("msg"), input.get("email_id"))
    assert expected_output.get("merchant") == transaction.merchant


@pytest.mark.parametrize("input,expected_output", DATA)
def test_transaction_payer_parsing(input, expected_output):
    """
    If the transaction is a deposit, ensure that the right payer is
    identified. If the transaction is a withdrawal, ensure that no payer is
    identified.
    """
    transaction = email_parser.main(input.get("msg"), input.get("email_id"))
    assert expected_output.get("payer") == transaction.payer


@pytest.mark.parametrize("input,expected_output", DATA)
def test_transaction_amount_parsing(input, expected_output):
    """
    Ensure that the correct amount is identified from the email. Also ensure
    that the format is 00.00
    """
    transaction = email_parser.main(input.get("msg"), input.get("email_id"))
    assert expected_output.get("amount") == transaction.amount


@pytest.mark.parametrize("input,expected_output", DATA)
def test_transaction_account_parsing(input, expected_output):
    """
    Ensure that the correct account is identified. The only bank that does not
    have multiple accounts is Chase.
    """
    transaction = email_parser.main(input.get("msg"), input.get("email_id"))
    assert expected_output.get("account") == transaction.account


@pytest.mark.parametrize("input,expected_output", DATA)
def test_transaction_balance_parsing(input, expected_output):
    """
    Ensure that the balance was identified. Chase and Discover do not provide
    balance information.
    """
    transaction = email_parser.main(input.get("msg"), input.get("email_id"))
    assert expected_output.get("balance") == transaction.balance


@pytest.mark.parametrize("input,expected_output", DATA)
def test_date_parsing(input, expected_output):
    """
    Ensure that the time the alert email was sent to outgoing@gmail.com is
    right. The time the email was forwarded to the mail server should not be
    recorded.
    """
    transaction = email_parser.main(input.get("msg"), input.get("email_id"))
    assert expected_output.get("date") == transaction.date
