"""
Tests inserting transactions (module sage/db/transactions.py).

The input is a transaction class object. Each object is created from the data
list defined below the imports.

The expected output is simply that the transaction can be
successfully inserted into the DB.
"""
import pytest

from sage.__main__ import main
from sage.db import transactions
from sage.models.transaction import Transaction
from tests import utils


def test_transaction_insert(etl_db_conn):
    """
    Ensure that all emails in the inbox are inserted into the transaction table.
    """
    utils.refresh_inbox("transaction_emails.mbox")
    msg_count = main()
    # Query to get the count of the emails table.
    with etl_db_conn, etl_db_conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                COUNT(*)
            FROM
                transactions
            """
        )
        for result in cursor.fetchall():
            inserted_count = result[0]
    assert msg_count.get("retrieved") == inserted_count


data = [
    (
        dict(
            date="2022-10-06",
            type_="transfer withdrawal",
            bank="Huntington",
            merchant=None,
            payer=None,
            amount="999.51",
            account="asterisk-free checking",
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
            account="asterisk-free checking",
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
            account="asterisk-free checking",
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
            account="asterisk-free checking",
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
            identical_txn_id=None,
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
