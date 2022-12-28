"""
Tests the email parser (module sage/email_parser/email_parser.py) to ensure it
correctly parses an  email into transaction data.

The input is the UID of the email, which maps to an email that was loaded
into the mail server when the docker container was created. These emails
are contained within the file
docker/mailserver/test_data/example_data/transaction_emails_development.mbox

They're also listed as separate files in
tests/test_email_parser/test_data/example_data so they can be more easily
viewed.

The expected expected_output is the transaction object defined in
sage/email_data/transaction.py
"""

import imap_tools
import pytest

from sage.email_parser import email_parser


def create_test_data():
    data = [
        (
            (dict(uid="3")),
            (
                dict(
                    uid=3,
                    transaction_time="2022-10-06 10:32:00",
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
            (dict(uid="14")),
            (
                dict(
                    uid=14,
                    transaction_time="2022-10-06 10:28:00",
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
            (dict(uid="5")),
            (
                dict(
                    uid=5,
                    transaction_time="2022-09-13 04:47:00",
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
            (
                dict(
                    uid="7",
                )
            ),
            (
                dict(
                    uid=7,
                    transaction_time="2022-08-08 04:31:00",
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
            (dict(uid="9")),
            (
                dict(
                    uid=9,
                    transaction_time="2022-10-06 10:39:00",
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
            (
                dict(
                    uid="11",
                )
            ),
            (
                dict(
                    uid=11,
                    transaction_time="2022-08-24 08:20:00",
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
            (dict(uid="17")),
            (
                dict(
                    uid=17,
                    transaction_time="2022-10-05 08:20:00",
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
            (dict(uid="19")),
            (
                dict(
                    uid=19,
                    transaction_time="2022-08-24 08:20:00",
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
            (dict(uid="21")),
            (
                dict(
                    uid=21,
                    transaction_time="2022-08-24 04:42:00",
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
    with imap_tools.MailBoxUnencrypted(pytest.IMAP4_FQDN).login(
        pytest.RECEIVING_EMAIL_USER, pytest.RECEIVING_EMAIL_PASSWORD
    ) as mailbox:
        for email in data:
            input = email[0]
            input_uid = input.get("uid")
            try:
                for msg in mailbox.fetch(imap_tools.AND(uid=[input_uid])):
                    input["msg"] = msg
            except Exception as error:
                print(f"No email having UID {input_uid} was found: {error}")
    return data


@pytest.mark.parametrize("input,expected_output", create_test_data())
def test_email_uid_parsing(input, expected_output):
    """
    Ensure the UID is correct and that it's an integer and not a string.
    """
    # Pass the msg object to the email parser
    transaction = email_parser.main(input.get("msg"))
    # Compare the transaction object to the expected expected_output
    assert expected_output.get("uid") == transaction.uid


# TODO: Add test emails for cash transactions
@pytest.mark.parametrize("input,expected_output", create_test_data())
def test_transaction_bank_parsing(input, expected_output):
    """
    Ensure the right bank was identified. The bank can be
    Huntington, Chase, Discover or cash.
    """
    transaction = email_parser.main(input.get("msg"))
    assert expected_output.get("bank") == transaction.bank


@pytest.mark.parametrize("input,expected_output", create_test_data())
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
    transaction = email_parser.main(input.get("msg"))
    assert expected_output.get("type_") == transaction.type_


@pytest.mark.parametrize("input,expected_output", create_test_data())
def test_transaction_merchant_parsing(input, expected_output):
    """
    If the transaction is a withdrawal, ensure that the right merchant is
    identified. If the transaction is a deposit, ensure that no merchant is
    identified.
    """
    transaction = email_parser.main(input.get("msg"))
    assert expected_output.get("merchant") == transaction.merchant


@pytest.mark.parametrize("input,expected_output", create_test_data())
def test_transaction_payer_parsing(input, expected_output):
    """
    If the transaction is a deposit, ensure that the right payer is
    identified. If the transaction is a withdrawal, ensure that no payer is
    identified.
    """
    transaction = email_parser.main(input.get("msg"))
    assert expected_output.get("payer") == transaction.payer


@pytest.mark.parametrize("input,expected_output", create_test_data())
def test_transaction_amount_parsing(input, expected_output):
    """
    Ensure that the correct amount is identified from the email. Also ensure
    that the format is 00.00
    """
    transaction = email_parser.main(input.get("msg"))
    assert expected_output.get("amount") == transaction.amount


@pytest.mark.parametrize("input,expected_output", create_test_data())
def test_transaction_account_parsing(input, expected_output):
    """
    Ensure that the correct account is identified. The only bank that does not
    have multiple accounts is Chase.
    """
    transaction = email_parser.main(input.get("msg"))
    assert expected_output.get("account") == transaction.account


@pytest.mark.parametrize("input,expected_output", create_test_data())
def test_transaction_balance_parsing(input, expected_output):
    """
    Ensure that the balance was identified. Chase and Discover do not provide
    balance information.
    """
    transaction = email_parser.main(input.get("msg"))
    assert expected_output.get("balance") == transaction.balance


@pytest.mark.parametrize("input,expected_output", create_test_data())
def test_transaction_time_parsing(input, expected_output):
    """
    Ensure that the time the alert email was sent to dev.kfike@gmail.com is
    right. The time the email was forwarded to the mail server should not be
    recorded.
    """
    transaction = email_parser.main(input.get("msg"))
    assert expected_output.get("transaction_time") == transaction.transaction_time
