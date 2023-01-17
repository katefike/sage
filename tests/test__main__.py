from sage.__main__ import main

"""
Tests the entrypoint of the program, __main__.py
"""


def test_unretrieved_email(delete_emails, send_email):
    """
    Send an email that isn't from the forwarding email.
    It should not be retrieved from the inbox.
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
    sender = "test.rejected.email@aol.com"
    send_email(html_body, sender)
    msg_count = main()
    assert msg_count.get("retrieved") == 0


def test_rejected_email(delete_emails, send_email):
    """
    Send an email that is from the forwarding email but doesn't have a body.
    It should be retrieved from the inbox, but then rejected.
    """
    send_email()
    msg_count = main()
    assert msg_count.get("retrieved") == 1
    assert msg_count.get("rejected") == 1


def test_unparsable_emails(delete_emails, fresh_inbox):
    """
    Send unparasble emails that are from the forwarding email and have bodies,
    but the contents are not transactions.
    They should be retrieved from the inbox and left unparsed.
    """

    fresh_inbox("unparsable_emails_development.mbox")
    msg_count = main()
    assert msg_count.get("retrieved") == 1
    assert msg_count.get("rejected") == 1
