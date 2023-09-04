from dataclasses import dataclass, field


@dataclass(init=True, repr=True)
class Email:
    """
    Represents an email forwarded to the mail server.
    """

    # pylint: disable=too-many-instance-attributes

    # Unique identifier; defined by Dovecot. Increments sequentially
    uid: int
    # Time the email was batch-processed and inserted into the DB
    # ISO 8601/RFC 3339 format; 1999-01-08 23:04:01
    batch_time: str
    # Date the email was forwarded by the fowarding email
    # and received by the mail server
    # ISO 8601/RFC 3339 format; 1999-01-08 23:04:01
    forwarded_date: str
    # The email From: line; it should always be the forwarding email
    from_: str
    # The email of the original sender; the financial instiution's email
    origin: str
    # The email Subject: line
    subject: str
    # Indicates if the email body is html or plain text
    html: str
    # The raw, unparsed email body
    body: str
