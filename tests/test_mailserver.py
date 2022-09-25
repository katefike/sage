def test_sending_single_email(send_single_email):
    """
    Test if emails are successfully sent via SMTP
    """
    assert send_single_email is True
