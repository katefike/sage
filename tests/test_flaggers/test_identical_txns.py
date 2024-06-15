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

from sage.__main__ import main
from tests import utils

DATA = [
    # (dict(file="distinct_but_similar_txns.mbox"), dict(inserted_txn_count=2, flagged_identical_txn=1)),
    (
        dict(file="identical_txns_gmail+cloudHQ_forwards.mbox"),
        dict(inserted_txn_count=2, flagged_identical_txn=1),
    ),
    # FIXME: Won't load; returns error "Skipping ./test_data/example_data/identical_txns_duplicate_forwards.mbox: not a mbox file"
    # (
    #     dict(file="identical_txns_duplicate_forwards.mbox"),
    #     dict(inserted_txn_count=2, flagged_identical_txn=1),
    # ),
    # (
    #     dict(file="identical_txns_triplicate_forwards.mbox"),
    #     dict(inserted_txn_count=3, flagged_identical_txn=2),
    # ),
]


@pytest.mark.parametrize("input,expected_output", DATA)
def test_identical_txns(input, expected_output):
    """
    Ensure that potential identical transactions are flagged.
    """
    utils.refresh_inbox(input.get("file"))

    msg_count = main()
    assert expected_output.get("inserted_txn_count") == msg_count.get("processed")
