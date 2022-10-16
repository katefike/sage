import os
import pathlib
import typing

import imap_tools
from dotenv import load_dotenv
from loguru import logger

from email_parser import email_parser

# from db import db_transactions

logger.add(sink="debug.log")


def main():
    """
    DOCSTRING EVENTUALLY
    """
    # Get all environment variables
    app_root = str(pathlib.Path(__file__).parent.parent)
    env_path = app_root + "/.env"
    if not load_dotenv(env_path):
        logger.critical(".env failed to load.")
    IMAP4_FQDN = os.environ.get("IMAP4_FQDN")
    FORWARDING_EMAIL = os.environ.get("FORWARDING_EMAIL")
    RECEIVING_EMAIL_USER = os.environ.get("RECEIVING_EMAIL_USER")
    RECEIVING_EMAIL_PASSWORD = os.environ.get("RECEIVING_EMAIL_PASSWORD")

    # Log into the receiving mailbox on the mail server and retrieve all messages
    # TODO: Refactor to only retrieve messages from the forwarding email
    # TODO: Refactor to only retrieve messages that haven't been parsed already
    with imap_tools.MailBoxUnencrypted(IMAP4_FQDN).login(
        RECEIVING_EMAIL_USER, RECEIVING_EMAIL_PASSWORD
    ) as mailbox:
        for msg in mailbox.fetch():
            # Ignore emails that aren't from the forwarding email
            if msg.from_ != FORWARDING_EMAIL:
                continue
            # Ignore emails that don't have a text or html body
            if not msg.text or msg.html:
                continue
            print(msg.uid, msg.to, msg.from_, msg.subject, msg.text, msg.html)
            parsed_email = email_parser.main(msg)

    # TODO: Write the emails to the db
    #     if parsed_email and parsed_email.get("transaction"):
    #         db_transactions.insert_transaction(parsed_email)
    #         logger.info("Success")
    #         # db_transactions.write_transaction(transaction)
    logger.info("DONE")
    return


if __name__ == "__main__":
    main()
