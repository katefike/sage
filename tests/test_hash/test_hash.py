"""
Tests hashing, which is a way to screen for duplicate transactions.

The input is a set of two or more emails. The emails may or may not represent
duplicate transactions.

The expected output is the failure or success of inserting a transaction.
For two similar, but distinct transactions, the output is two inserted
transactions.
For duplicate transactions (e.g. from the same transaction forwarded twice)
the output is one inserted transaction.
"""
import pytest

from sage.db import transactions
from sage.models.email import Email
from tests import utils


def get_test_data():
    data = [
        # (dict(file="distinct_but_similar_txns.mbox"), dict(insert_count=2)),
        (dict(file="duplicate_txns_gmail+cloudHQ_forwards.mbox"), dict(insert_count=1)),
        (dict(file="duplicate_txns_identical_forwards.mbox"), dict(insert_count=1)),
    ]

    # Retrieve the email corresponding to the UID
    for email in data:
        input = email[0]
        uid = input.get("uid")
        msgs = utils.get_inbox_emails(uid)
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


@pytest.mark.parametrize("input,expected_output", DATA)
def test_hash(input, expected_output):
    """
    Ensure that duplicate transactions are rejected based on the hash value.
    """
    # transaction = email_parser.main(input.get("msg"), input.get("email_id"))
    # assert expected_output.get("bank") == transaction.bank
