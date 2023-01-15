"""
Tests the mailserver container called sage-mailserver-1.
"""


def test_sending_single_email(send_email):
    """
    Test if emails are successfully sent via SMTP
    """

    html_body = """\
    <html>
    <head></head>
    <body>
        <p>Hi!<br>
        This is a single test email.
        </p>
    </body>
    </html>
    """
    success = send_email(html_body)
    assert success is True


def test_getting_emails(total_emails):
    """
    Test if emails can be retrieved via IMAP.
    """
    assert len(total_emails) != 0
