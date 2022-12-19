"""
Tests the module sage/email_parser/email_parser.py
"""

import pathlib

import pytest

from sage.email_data.transaction import Transaction
from sage.email_parser import email_parser


def create_test_data():
    dir = str(pathlib.Path(__file__).parent)
    path = f"{dir}/test_data/example_data"
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
            (dict(uid="5", date_str="Thu, 13 Oct 2022 23:36:32 -0400")),
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
            (dict(uid="19", date_str="Thu, 13 Oct 2022 23:52:07 -0400")),
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

    for case in data:
        input = case[0]
        uid = input.get("uid")
        text_file = open(f"{path}/uid_{uid}.txt", "r")
        text_data = text_file.read()
        text_file.close()
        case[0]["text"] = text_data
    return data


@pytest.mark.parametrize("input,output", create_test_data())
def test_email_parser(input, output):
    """
    Test the email parser to ensure it correctly parses emails into
    transaction data.

    expected = uid, transaction_time, type_, bank, merchant,
    payer, raw_amount, account, balance
    """
    # Pass the msg object to the email parser
    transaction = email_parser.main(input)
    # Compare the transaction object to the expected output

    uid = str
    assert uid == "1"


if __name__ == "__main__":
    create_test_data()
