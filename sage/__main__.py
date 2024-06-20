"""
This is starting point of the program. It steps through the following
tasks:

1. Load the environment variables.
2. Log into the email account on the mail server that is receiving the
forwarded alert emails. Retrieve emails that are from the forwarding email.
3. Store all retrieved emails in the database's emails table.
4. Process the transaction data contained in the email message:
    4a. Parse the transaction data from the email message.
    4b. If needed, flag identical transactions.
    4c. Write the transaction data to the Postgres database.
"""
import sys

from loguru import logger

from sage.db import emails, transactions
from sage.flaggers import identical_txns
from sage.models.email import Email
from sage.mx import get_emails
from sage.parsers import email_parser

from . import ENV

logger.add(sink="sage_main.log", level="INFO")


def main(retry_unparsed_emails=False):
    logger.info("STARTING SAGE")
    msg_count = {
        "retrieved": 0,
        "unparsed": 0,
        "processed": 0,
    }

    # Log into the receiving mailbox on the mail server and retrieve emails
    # that are from the forwarding email
    # Connect to the mailbox containing transaction alert emails
    from_forwarding_email = True
    retrieved_emails = get_emails.main(from_forwarding_email, retry_unparsed_emails)

    for msg in retrieved_emails:
        msg_count["retrieved"] = msg_count.get("retrieved", 0) + 1
        # Store the retrieved email in the database's emails table
        email_id = emails.insert_email(msg)

        # Parse a email message into the txn data
        txn = email_parser.main(msg, email_id)
        logger.info(f"Email UID {msg.uid} - attempting to parse...")
        if not txn:
            logger.info(f"Email UID {msg.uid} - unparsed.")
            msg_count["unparsed"] = msg_count.get("unparsed", 0) + 1
            continue

        # Check if there's an identical txn in the DB already
        # If so, flag it
        flagged_txn = identical_txns.main(txn)

        # Write the txn to the database
        transactions.insert_transaction(flagged_txn)  # pragma: no cover
        logger.info(f"Email UID {msg.uid} - successfully parsed!")

        # One down!
        msg_count["processed"] = msg_count.get("processed", 0) + 1  # pragma: no cover

    deduced_msg_count = msg_count.get("unparsed") + msg_count.get("processed")
    retrieved_msg_count = msg_count.get("retrieved")
    if deduced_msg_count != msg_count.get("retrieved"):  # pragma: no cover
        logger.critical(
            f"FAILED: {retrieved_msg_count} msgs retrieved but {deduced_msg_count} were accounted for."
        )
    logger.info(f"Total Messages in Batch = {retrieved_msg_count}")
    logger.info(f"{msg_count}")
    logger.info("DONE")
    return msg_count


if __name__ == "__main__":  # pragma: no cover
    retry_unparsed_emails = sys.argv[1]
    msg_count = main(retry_unparsed_emails)
