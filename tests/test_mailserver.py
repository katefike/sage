def test_sending_accepted_email(send_accepted_email):
    """
    Test if emails from authorized the authoized sender is successfully sent via SMTP.
    """
    assert send_accepted_email is True


def test_sending_rejected_email(send_rejected_email):
    """
    Test if emails from an unauthorized sender is rejected.
    """
    assert send_rejected_email is False


def test_getting_emails(get_emails):
    """
    Test if emails can be retrieved via IMAP.
    """
    assert len(get_emails) is not 0
