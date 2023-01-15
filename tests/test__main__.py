from sage.__main__ import main

"""
Tests the entrypoint of the program, __main__.py
"""


def test_unretrieved_email(delete_all_emails, send_email):
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
