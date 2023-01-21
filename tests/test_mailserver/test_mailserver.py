"""
Tests the mailserver container called sage-mailserver-1.
"""
from tests import utils


def test_sending_single_email():
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
    success = utils.send_email(html_body)
    assert success is True


def test_getting_emails():
    """
    Test if emails can be retrieved via IMAP.
    """
    msgs = utils.get_emails()
    assert len(msgs) != 0
