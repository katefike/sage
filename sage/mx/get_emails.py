import pprint
from datetime import datetime
from typing import Iterator, List, Optional

import imap_tools
from bs4 import BeautifulSoup
from loguru import logger

from sage.db import emails
from sage.models.email import Email

from . import ENV

logger.add(sink="sage_main.log")


def main(
    filter: Optional[str] = None,
    pls_print: Optional[bool] = False,
) -> List[Email]:
    with open_mailbox() as mailbox:
        if filter == "forwarded":
            logger.info(
                f"Only getting emails from FORWARDING_EMAIL {ENV['FORWARDING_EMAIL']}..."
            )
            msgs = mailbox.fetch(imap_tools.A(from_=ENV["FORWARDING_EMAIL"]))

        elif filter == "unparsed":
            logger.info(
                "Only getting emails that are in the DB table named emails,\
                but don't have an associated txn..."
            )
            msgs = []
            records, columns_ = emails.get_unparsed_emails()
            for record in records:
                uid_ = record[1]
                retrieved_msg = mailbox.fetch(imap_tools.AND(uid=[str(uid_)]))
                for msg in retrieved_msg:
                    msgs.append(msg)

        elif filter and "uid=" in filter:
            uid_parts = filter.split("=")
            uid_ = uid_parts[1]
            logger.info(f"Only getting email uid {uid_}...")
            msgs = mailbox.fetch(imap_tools.AND(uid=[uid_]))
            if msgs is None:
                logger.critical(f"No email was retrieved for email UID {uid_}...")
                return
        else:
            logger.info("Getting all emails from inbox...")
            msgs = mailbox.fetch()

        emails_ = transform_MailMessages_to_Emails(msgs)

        if pls_print:
            pprint.pp(emails_)

        logger.info(f"{len(emails_)} email(s) retrieved.")

        return emails_


def open_mailbox() -> imap_tools.BaseMailBox:
    try:
        mailbox = imap_tools.MailBoxUnencrypted("localhost").login(
            ENV["RECEIVING_EMAIL_USER"], ENV["RECEIVING_EMAIL_PASSWORD"]
        )
        return mailbox
    except imap_tools.ImapToolsError as error:  # pragma: no cover
        logger.critical(f"Failed to open mailbox: {error}")
        raise error


def transform_MailMessages_to_Emails(
    msgs: Iterator[imap_tools.MailMessage],
) -> List[Email]:
    emails_ = []

    # Set the time the batch started
    utc_timestamp = datetime.utcnow()
    batch_time = utc_timestamp.strftime("%Y-%m-%d %H:%M:%S")

    for msg in msgs:
        # FIXME: Add origin to the emails table #157
        origin = "placeholder"
        if msg.html:
            html = "true"
            soup = BeautifulSoup(msg.html, "html.parser")
            body = soup.get_text(" ")
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
        emails_.append(email)

    return emails_
