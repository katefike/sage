"""
Tests the entrypoint of the program, __main__.py
"""
from sage.__main__ import main

from . import utils


def test_unretrieved_email():
    """
    Send an email that isn't from the forwarding email.
    It should not be retrieved from the inbox.
    """
    utils.delete_emails()
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
    sender = "test.unretrieved.email@aol.com"
    utils.send_email(html_body, sender)
    msg_count = main()
    assert msg_count.get("retrieved") == 0


def test_unparsable_emails():
    """
    Send unparasble emails that are from the forwarding email and have bodies,
    but the contents are not transactions.
    They should be retrieved from the inbox and left unparsed.
    """

    utils.fresh_inbox("unparsable_emails.mbox")
    msg_count = main()
    assert msg_count.get("retrieved") == msg_count.get("unparsed")
