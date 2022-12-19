"""
Tests the module sage/email_parser/email_parser.py
"""

import pathlib

import pytest
from imap_tools import MailMessage

from sage.email_data.transaction import Transaction
from sage.email_parser import email_parser


def create_test_data():
    data = [
        (
            (
                dict(
                    uid="1",
                )
            ),
            (
                dict(
                    uid=1,
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
            (
                dict(
                    uid="3",
                )
            ),
            (
                dict(
                    uid=3,
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
            (dict(uid="5")),
            (
                dict(
                    uid=5,
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
            (dict(uid="7")),
            (
                dict(
                    uid=7,
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
            (dict(uid="9")),
            (
                dict(
                    uid=9,
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
            (dict(uid="11")),
            (
                dict(
                    uid=11,
                    transaction_time="2022-08-24 04:42:00",
                    type_="deposit",
                    bank="Huntington",
                    merchant=None,
                    payer="CHASE CREDIT CRD RWRD RDM",
                    amount="17.09",
                    naccount="checking",
                    balance="257.06",
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
                    balance="20,000.00",
                )
            ),
        ),
        (
            (dict(uid="17")),
            (
                dict(
                    uid=17,
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
    ]

    dir = str(pathlib.Path(__file__).parent)
    path = f"{dir}/test_data/example_data"

    for email in data:
        input = email[0]
        uid = input.get("uid")
        text_file = open(f"{path}/uid_{uid}.txt", "r")
        text_data = text_file.read()
        text_file.close()
        email[0]["text"] = text_data
    return data


@pytest.mark.parametrize("input,output", create_test_data())
def test_email_parser(input, output):
    """
    Test the email parser to ensure it correctly parses emails into
    transaction data.

    The input is the UID of the email, which maps to the email file name.
    EX) uid_1.txt contains a forwarded email with the UID 1

    The expected output is the transaction object defined in
    sage/email_data/transaction.py

    expected = uid, transaction_time, type_, bank, merchant,
    payer, account, balance
    """
    # Pass the msg object to the email parser
    input = MailMessage
    transaction = email_parser.main(input)
    # Compare the transaction object to the expected output
    uid = input.get("uid")
    assert uid == "1"


if __name__ == "__main__":
    create_test_data()
