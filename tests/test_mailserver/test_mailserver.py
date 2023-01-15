"""
Tests the mailserver container called sage-mailserver-1.
"""


def test_sending_single_email(send_non_transaction_email):
    """
    Test if emails are successfully sent via SMTP
    """
    assert send_non_transaction_email is True


def test_getting_emails(total_emails):
    """
    Test if emails can be retrieved via IMAP.
    """
    assert len(total_emails) != 0
