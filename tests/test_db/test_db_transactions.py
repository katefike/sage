"""
Tests inserting transactions (module sage/db/transactions.py).

The input is a transaction class object.

They're also listed as separate files in
tests/test_parsers/test_data/example_data so they can be more easily
viewed.

The expected expected_output is the transaction object defined in
sage/models/transaction.py
"""
import pytest

from sage.db import transactions
from sage.models.transaction import Transaction
from tests import utils

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
        transaction = Transaction(
            email_id=0,
            id=None,
            date=transaction_dict.get("date"),
            type_=transaction_dict.get("type_"),
            bank=transaction_dict.get("bank"),
            merchant=transaction_dict.get("merchant"),
            payer=transaction_dict.get("payer"),
            amount=transaction_dict.get("amount"),
            account=transaction_dict.get("account"),
            balance=transaction_dict.get("balance"),
            hash=None,
        )
        input.append(transaction)
    return input


@pytest.mark.parametrize("input", create_transaction_objects())
def test_insert_transaction(input):
    """
    Ensure that a transaction can be inserted into the transaction table.
    """
    email_id = utils.insert_db_email()
    input.email_id = email_id
    row_count = transactions.insert_transaction(input)
    # The number of rows inserted will be returned if the insert was successful
    assert 1 == row_count


email_data = [
    dict(
        uid=1,
        batch_time="2023-08-31 15:22:40",
        forwarded_date="2023-08-31",
        from_="outgoing@gmail.com",
        origin="bank@example.com",
        subject="Example Transaction Email",
        html="f",
        body="Hello world!",
    )
]


# def create_email_objects() -> List:
#     input = []
#     for email_dict in email_data:
#         email = Email(
#             0,
#             None,
#             email_dict.get("uid"),
#             email_dict.get("batch_time"),
#             email_dict.get("forwarded_date"),
#             email_dict.get("from_"),
#             email_dict.get("origin"),
#             email_dict.get("subject"),
#             email_dict.get("html"),
#             email_dict.get("body"),
#         )
#         input.append(email)
#     return input


# @pytest.mark.parametrize("input", create_email_objects())
# def test_duplicate_email_forwards(input):
#     """
#     Ensure that if the same transaction email is forwarded twice,
#     the result is only one transaction.
#     """
#     email_id = utils.insert_db_email(input)
#     input.email_id = email_id
#     row_count = transactions.insert_transaction(input)
#     # The number of rows inserted will be returned if the insert was successful
#     assert 1 == row_count
