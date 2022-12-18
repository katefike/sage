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
    logger.info("STARTING SAGE")
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
            total_messages_count = 0
            rejected_messages_count = 0
            unparsed_messages_count = 0
            unwritten_transactions_count = 0
            processed_transactions_count = 0
            for msg in mailbox.fetch():
                total_messages_count = total_messages_count + 1
                # Ignore emails that aren't from the forwarding email
                # FIXME: The emails loaded from transaction_emails_development.mbox have
                # msg.from_ = bank's alert email address
                # not the forwarding email
                if msg.from_ != FORWARDING_EMAIL:
                    logger.info(f"Rejecting email from {msg.from_}. The mail server is only accepting emails from {FORWARDING_EMAIL}.")
                    rejected_messages_count = rejected_messages_count + 1
                    continue
                # Ignore emails that don't have a text or html body
                if not msg.text or not msg.html:
                    logger.info(f"Rejecting email from {msg.from_} because it doesn't have a message body.")
                    rejected_messages_count = rejected_messages_count + 1
                    continue

                # Parse a email message into the transaction data
                try:
                    transaction = email_parser.main(msg)
                except Exception as error:
                    logger.info("FAILED")
                    logger.critical(f"EMAIL PARSER ERROR: Failed to parse msg UID {msg.uid}: {error}")
                    unparsed_messages_count = unparsed_messages_count + 1
                logger.info(transaction)

                # FIXME: Write the emails to the db
                # unwritten_transactions_count = unwritten_transactions_count + 1
                
                # One down!
                processed_transactions_count = processed_transactions_count + 1

            deduced_total_messages_count = rejected_messages_count + unparsed_messages_count + unwritten_transactions_count + processed_transactions_count
            if deduced_total_messages_count != total_messages_count:
                logger.critical("FAILED")
                logger.critical(f"ERROR-HANDLING ERROR: {total_messages_count} messages were retrieved from the mail server, but only {deduced_total_messages_count} were accounted for.")
            logger.info(f"Total Messages in Batch = {total_messages_count}")
            logger.info(f"Rejected Messages = {rejected_messages_count}")
            logger.info(f"Unparsed Messages = {unparsed_messages_count}")
            # logger.info(f"Unwritten Transactions = {unwritten_transactions_count}")
            logger.info(f"Processed Transactions = {processed_transactions_count}")
            logger.info("DONE")
            return

    except Exception as error:
        logger.critical("FAILED")
        logger.critical(f"MAILSERVER ERROR: Failed to connect via IMAP to the inbox of user {RECEIVING_EMAIL_USER}: {error}")
        return


if __name__ == "__main__":
    main()
