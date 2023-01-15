from sage.__main__ import main

"""
Tests the entrypoint of the program, __main__.py
"""


def test_rejected_email(delete_all_emails, send_non_transaction_email):
    """Send an email that isn't from the forwarding email"""
    msg_count = main()
    assert msg_count.get("retrieved") == 1
    assert msg_count.get("rejected") == 0
