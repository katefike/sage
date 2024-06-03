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
import os

import pytest

from sage.db import transactions
from tests import utils

DATA = [
    # (dict(file="distinct_but_similar_txns.mbox"), dict(inserted_txn_count=2)),
    (
        dict(file="duplicate_txns_gmail+cloudHQ_forwards.mbox"),
        dict(inserted_txn_count=1),
    ),
    (dict(file="duplicate_txns_identical_forwards.mbox"), dict(inserted_txn_count=1)),
]


@pytest.mark.parametrize("input,expected_output", DATA)
def test_hash(input, expected_output):
    """
    Ensure that duplicate transactions are rejected based on the hash value.
    """
    utils.fresh_inbox(input.get("file"))
    from sage.__main__ import main

    msg_count = main()
    assert expected_output.get("inserted_txn_count") == msg_count.get("processed")
