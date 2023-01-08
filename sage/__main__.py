import os
import pathlib

import imap_tools
from db import transactions
from dotenv import load_dotenv
from email_parser import email_parser
from loguru import logger

logger.add(sink="debug.log", level="INFO")


def main():
    """
    This is starting point of the program. It steps through the following
    tasks:

    1. Load the environment variables.
    2. Query the database to retrieve the maximum UID. According to RFC9051:
    "Unique identifiers are assigned in a strictly ascending fashion in the
    mailbox; as each message is added to the mailbox, it is assigned a
    higher UID than those of all message(s) that are already in the
    mailbox.  Unlike message sequence numbers, unique identifiers are not
    necessarily contiguous."
    3. Log into the email account on the mail server that is receiving the
    forwarded alert emails. Retrieve emails that have a UID greater than the
    maximum UID in the database.
    4. Skip emails that are not from the forwarding email or don't have a body.
    5. Process the transaction data contained in the email message:
        5a. Parse the transaction data from the email message.
        5b. Write the transaction data to the Postgres database.
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

    # Log into the receiving mailbox on the mail server and retrieve emails
    # that have a UID that is greater than the maximum UID in the database.
    max_uid = transactions.get_maximum_uid()
    try:
        with imap_tools.MailBoxUnencrypted(IMAP4_FQDN).login(
            RECEIVING_EMAIL_USER, RECEIVING_EMAIL_PASSWORD
        ) as mailbox:
            total_messages_count = 0
            rejected_messages_count = 0
            unparsed_messages_count = 0
            unwritten_transactions_count = 0
            processed_transactions_count = 0
            # Retrieve emails that are greater than the maximum UID
            # and are from the forwarding email
            for msg in mailbox.fetch(
                imap_tools.A(
                    uid=imap_tools.U(f"{max_uid + 1}", "*"), from_=FORWARDING_EMAIL
                )
            ):
                total_messages_count = total_messages_count + 1
                # Ignore emails that don't have a text or html body
                # This seems unlikely but who knows
                if not msg.text or not msg.html:
                    logger.warning(
                        f"Rejecting email from {msg.from_} because it doesn't have a message body."
                    )
                    rejected_messages_count = rejected_messages_count + 1
                    continue
                # Parse a email message into the transaction data
                transaction = email_parser.main(msg)
                if not transaction.amount:
                    logger.info(
                        f"UID {msg.uid} was not parsed into a \
                        transaction."
                    )
                    unparsed_messages_count = unparsed_messages_count + 1
                    continue
                row_count = transactions.insert_transaction(transaction)
                if row_count != 1:
                    unwritten_transactions_count = unwritten_transactions_count + 1
                    continue

                # One down!
                processed_transactions_count = processed_transactions_count + 1

            deduced_total_messages_count = (
                rejected_messages_count
                + unparsed_messages_count
                + unwritten_transactions_count
                + processed_transactions_count
            )
            if deduced_total_messages_count != total_messages_count:
                logger.critical("FAILED")
                logger.critical(
                    f"ERROR-HANDLING ERROR: {total_messages_count} messages were retrieved from the mail server, but only {deduced_total_messages_count} were accounted for."
                )
            logger.info(f"Total Messages in Batch = {total_messages_count}")
            logger.info(f"Rejected Messages = {rejected_messages_count}")
            logger.info(f"Unparsed Messages = {unparsed_messages_count}")
            logger.info(f"Processed Transactions {processed_transactions_count}")
            logger.info("DONE")
            return

    except Exception as error:
        logger.critical("FAILED")
        logger.critical(
            f"MAILSERVER ERROR: Failed to connect via IMAP to the \
            inbox of user {RECEIVING_EMAIL_USER}: {error}"
        )
        return


if __name__ == "__main__":
    main()
