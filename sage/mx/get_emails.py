from datetime import datetime
from typing import List, Optional

import imap_tools
from loguru import logger

from . import ENV

logger.add(sink="sage_main.log")

logger.info(f"FORWARDING_EMAIL: {ENV['FORWARDING_EMAIL']}")

# Set the time the batch started
utc_timestamp = datetime.utcnow()
batch_time = utc_timestamp.strftime("%Y-%m-%d %H:%M:%S")


def open_mailbox():
    try:
        mailbox = imap_tools.MailBoxUnencrypted("localhost").login(
            ENV["RECEIVING_EMAIL_USER"], ENV["RECEIVING_EMAIL_PASSWORD"]
        )
        return mailbox
    except imap_tools.ImapToolsError as error:  # pragma: no cover
        logger.critical(f"Failed to open mailbox: {error}")
        raise error


def get_emails():
    mailbox = open_mailbox()
    return
