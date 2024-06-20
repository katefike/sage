import pprint
from datetime import datetime
from typing import List, Optional

import imap_tools
from loguru import logger

from sage.models.email import Email

from . import ENV

logger.add(sink="sage_main.log")


def open_mailbox() -> imap_tools.BaseMailBox:
    try:
        mailbox = imap_tools.MailBoxUnencrypted("localhost").login(
            ENV["RECEIVING_EMAIL_USER"], ENV["RECEIVING_EMAIL_PASSWORD"]
        )
        return mailbox
    except imap_tools.ImapToolsError as error:  # pragma: no cover
        logger.critical(f"Failed to open mailbox: {error}")
        raise error


def main(
    filter: Optional[str] = None,
    pls_print: Optional[bool] = False,
) -> List[Email]:
    mailbox = open_mailbox()

    if filter == "forwarded":
        logger.info(
            f"Only getting emails from FORWARDING_EMAIL {ENV['FORWARDING_EMAIL']}..."
        )
        msgs = mailbox.fetch(imap_tools.A(from_=ENV["FORWARDING_EMAIL"]))
    elif filter == "unparsed":
        logger.info(
            "Only getting emails that are in the DB table named emails, \
            but don't have an associated txn..."
        )
    elif filter and "uid=" in filter:
        uid_parts = filter.split("=")
        uid_ = uid_parts[1]
        logger.info(f"Only getting email uid {uid_}...")
        msgs = mailbox.fetch(imap_tools.AND(uid=[uid_]))
    else:
        logger.info("Getting all emails from inbox...")
        msgs = mailbox.fetch()

    # Ultimately returned messages
    emails = []

    # Set the time the batch started
    utc_timestamp = datetime.utcnow()
    batch_time = utc_timestamp.strftime("%Y-%m-%d %H:%M:%S")

    # FIXME: type msg as class imap_tools.MailMessage
    for msg in msgs:
        # FIXME: Add origin to the emails table #157
        origin = "placeholder"
        # FIXME: body is set twice: once below and once in email_parser
        if msg.html:
            html = "true"
            body = msg.html
        elif msg.text:
            html = "false"
            body = msg.text
        email = Email(
            int(msg.uid),
            batch_time,
            msg.date,
            msg.from_,
            origin,
            msg.subject,
            html,
            body,
        )
        emails.append(email)

    if pls_print:
        pprint.pp(emails)

    logger.info(f"{len(emails)} email(s) retrieved.")

    return emails
