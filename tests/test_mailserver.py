def test_sending_single_email(send_single_email):
    """
    Test if emails are successfully sent via SMTP
    """
    assert send_single_email is True


def test_getting_emails(get_emails):
    """
    Test if emails can be retrieved via IMAP.
    """
    assert len(get_emails) is not 0
    assert len(get_emails) == 123456789
