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


def create_email_objects() -> List:
    input = []
    for email_dict in email_data:
        email = Email(
            0,
            None,
            email_dict.get("uid"),
            email_dict.get("batch_time"),
            email_dict.get("forwarded_date"),
            email_dict.get("from_"),
            email_dict.get("origin"),
            email_dict.get("subject"),
            email_dict.get("html"),
            email_dict.get("body"),
        )
        input.append(email)
    return input


@pytest.mark.parametrize("input", create_email_objects())
def test_duplicate_email_forwards(input):
    """
    Ensure that if the same transaction email is forwarded twice,
    the result is only one transaction.
    """
    email_id = utils.insert_db_email(input)
    input.email_id = email_id
    row_count = transactions.insert_transaction(input)
    # The number of rows inserted will be returned if the insert was successful
    assert 1 == row_count
