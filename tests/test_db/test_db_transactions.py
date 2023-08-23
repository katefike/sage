"""
Tests inserting transactions (module sage/db/transactions.py).

The input is a transaction class object.

They're also listed as separate files in
tests/test_email_parser/test_data/example_data so they can be more easily
viewed.

The expected expected_output is the transaction object defined in
sage/email_data/transaction.py
"""
import pytest

from sage.db import transactions
from sage.email_data.transaction import Transaction

data = [
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
]


def create_transaction_objects():
    input = []
    for transaction_dict in data:
        transaction_obj = Transaction(
            transaction_dict.get("date"),
            transaction_dict.get("type_"),
            transaction_dict.get("bank"),
            transaction_dict.get("merchant"),
            transaction_dict.get("payer"),
            transaction_dict.get("amount"),
            transaction_dict.get("account"),
            transaction_dict.get("balance"),
        )
        input.append(transaction_obj)
    return input


@pytest.mark.parametrize("input", create_transaction_objects())
def test_insert_transaction(input):
    """
    Ensure that a transaction can be inserted into the transaction table.
    """
    row_count = transactions.insert_transaction(input)
    # The number of rows inserted will be returned if the insert was successful
    assert 1 == row_count
