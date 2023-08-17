"""

"""
import pytest

from sage.__main__ import main
from tests import utils


def test_email_insert():
    """
    Ensure that all emails in the inbox are inserted into the emails table.
    """
    utils.fresh_inbox("transaction_emails.mbox")
    msg_count = main()
    assert msg_count.get("retrieved") == msg_count.get("unparsed")
