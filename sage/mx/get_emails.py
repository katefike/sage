import pprint
import re
from datetime import datetime
from typing import Iterator, List, Optional, Tuple, Set

import imap_tools
from bs4 import BeautifulSoup
from loguru import logger

from sage.db import emails
from sage.models.email import Email
from sage.parsers.utils import RegexError

from . import ENV, BANKS_CONFIG

logger.add(sink="sage_main.log")


def get_banks_config_email_addresses() -> Set:
    """
    Creates a set (unique list) of bank emails in BANKS_CONFIG
    """
    all_banks_addresses = []
    for bank in BANKS_CONFIG.values():
        all_banks_addresses.extend(bank['email_addresses'])
    unique_banks_email_addresses = set(all_banks_addresses)
    return unique_banks_email_addresses


def main(
    filter: Optional[str] = None,
    pls_print: Optional[bool] = False,
) -> List[Email]:
    with open_mailbox() as mailbox:
        if filter == "forwarded":
            all_email_addresses = {ENV['FORWARDING_EMAIL']}
            banks_email_addresses = get_banks_config_email_addresses()
            all_email_addresses.update(banks_email_addresses)
            logger.info(
                f"""
                Only getting emails from FORWARDING_EMAIL and bank_config.yml email addresses:
                {all_email_addresses}
                """
            )
            msgs = mailbox.fetch(imap_tools.OR(from_=all_email_addresses))

        elif filter == "unparsed":
            logger.info(
                "Only getting emails that are in the DB table named emails, but don't have an associated txn..."
            )
            msgs = []
            records, _columns = emails.get_unparsed_emails()
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
            if msgs is None:  # pragma: no cover
                logger.critical(f"No email was retrieved for email UID {uid_}...")
                return
        else:
            logger.info("Getting all emails from inbox...")
            msgs = mailbox.fetch()

        emails_ = transform_MailMessages_to_Emails(msgs)

        if pls_print:  # pragma: no cover
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


def get_manual_forward_origin(
    msg: imap_tools.MailMessage,
    body: str
) -> Tuple[bool, str]:
    # If an email was manually forwarded, parse the origin from the body
    # fwd_pattern = r"---------- Forwarded message ---------"
    fwd_pattern = r"Fwd: "
    fwd_match = re.search(fwd_pattern, msg.subject, flags=re.DOTALL | re.MULTILINE)
    if fwd_match:
        manually_forwarded = True
        origin_pattern = r"From: .* \<(.*)\>\s?\n?Date:"
        origin_match = re.search(origin_pattern, body, flags=re.DOTALL | re.MULTILINE)
        if origin_match:
            origin_raw = origin_match.group(1)
            from_ = origin_raw.strip()
        else:
            raise RegexError(f"Failed to parse origin from manually forwarded email with UID {msg.uid}")
    else:
        manually_forwarded = False
        from_ = msg.from_
    return manually_forwarded, from_


def transform_MailMessages_to_Emails(
    msgs: Iterator[imap_tools.MailMessage],
) -> List[Email]:
    emails_ = []

    # Set the time the batch started
    utc_timestamp = datetime.utcnow()
    batch_time = utc_timestamp.strftime("%Y-%m-%d %H:%M:%S")

    for msg in msgs:
        if msg.html:
            html = "true"
            soup = BeautifulSoup(msg.html, "html.parser")
            body = soup.get_text(" ").strip()
            body = re.sub(r"\s+", " ", body).strip()
        elif msg.text:
            html = "false"
            body = msg.text.strip()

        manually_forwarded, from_= get_manual_forward_origin(msg, body)

        email = Email(
            int(msg.uid),
            batch_time,
            msg.date,
            manually_forwarded,
            from_,
            msg.subject,
            html,
            body,
        )
        emails_.append(email)
    return emails_