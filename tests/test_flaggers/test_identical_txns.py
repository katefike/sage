"""
Tests flagging of identical txns.

The input is a set of two or more emails. The emails may or may not represent
identical txns.

There are two expected outputs:
    1. Every email results in an inserted txn.
    2. A count of identical txns.
"""
import pytest

from sage.__main__ import main
from sage.db import transactions
from tests import utils

DATA = [
    (
        dict(file="identical_txns_gmail+cloudHQ_forwards.mbox"),
        dict(inserted_txn_count=2, identical_txn_count=1),
    ),
    (
        dict(file="identical_txns_2_cloudHQ_forwards.mbox"),
        dict(inserted_txn_count=2, identical_txn_count=1),
    ),
]


@pytest.mark.parametrize("input,expected_output", DATA)
def test_identical_txns(input, expected_output):
    """
    Verify that identical transactions are flagged.
    """
    utils.refresh_inbox(input.get("file"))

    msg_count = main()
    assert expected_output.get("inserted_txn_count") == msg_count.get("processed")
    rows = transactions.get_identical_txns()
    assert expected_output.get("identical_txn_count") == len(rows)
