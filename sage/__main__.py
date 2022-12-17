import os
import pathlib
import typing

import imap_tools
from dotenv import load_dotenv
from loguru import logger

from sage.email_parser import email_parser

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
        logger.critical(f"ENVIRONMENT ERROR: .env failed to load from {env_path}")
    IMAP4_FQDN = os.environ.get("IMAP4_FQDN")
    FORWARDING_EMAIL = os.environ.get("FORWARDING_EMAIL")
    RECEIVING_EMAIL_USER = os.environ.get("RECEIVING_EMAIL_USER")
    RECEIVING_EMAIL_PASSWORD = os.environ.get("RECEIVING_EMAIL_PASSWORD")

    # Log into the receiving mailbox on the mail server and retrieve all messages
    # FIXME: Only retrieve messages that haven't been parsed already
    try:
        with imap_tools.MailBoxUnencrypted(IMAP4_FQDN).login(
            RECEIVING_EMAIL_USER, RECEIVING_EMAIL_PASSWORD
        ) as mailbox:
            for msg in mailbox.fetch():
                # Ignore emails that aren't from the forwarding email
                # FIXME: The emails loaded from transaction_emails_development.mbox have
                # msg.from_ = bank's alert email address
                # not the forwarding email
                if msg.from_ != FORWARDING_EMAIL:
                    logger.info(f"Rejecting email from {msg.from_}")
                    continue
                # Ignore emails that don't have a text or html body
                if not msg.text or not msg.html:
                    continue

                # Parse a email message into the transaction data
                try:
                    transaction = email_parser.main(msg)
                except Exception as error:
                    logger.info("FAILED")
                    logger.critical(f"EMAIL PARSER ERROR: Failed to parse msg UID {msg.uid}.")
                print(transaction)
                logger.info(transaction)

                # FIXME: Write the emails to the db
                #     if parsed_email and parsed_email.get("transaction"):
                #         db_transactions.insert_transaction(parsed_email)
                #         logger.info("Success")
                #         # db_transactions.write_transaction(transaction)
                logger.info("DONE")
                return True
    except Exception as error:
        logger.critical("FAILED")
        logger.critical(f"MAILSERVER ERROR: Failed to connect via IMAP to the inbox of user {RECEIVING_EMAIL_USER}.")
        return False


if __name__ == "__main__":
    main()
