"""
This is starting point of the program. It steps through the following
tasks:

1. Load the environment variables.
2. Log into the email account on the mail server that is receiving the
forwarded alert emails. Retrieve emails that are from the forwarding email.
3. Store all retrieved emails in the database's emails table.
4. Process the transaction (txn) data contained in the email message:
    4a. Parse the txn data from the email message.
    4b. If needed, flag identical txns.
    4c. Write the txn data to the Postgres database.
"""
import sys

from loguru import logger

from sage.db import emails, txns
from sage.flaggers import identical_txns
from sage.mx import get_emails
from sage.parsers import email_parser

logger.add(sink="sage_main.log", level="INFO")


def main(retry_unparsed_emails=False):
    logger.info("STARTING SAGE")
    email_count = {
        "retrieved": 0,
        "unparsed": 0,
        "processed": 0,
    }

    # Log into the receiving mailbox on the mail server and retrieve emails
    if retry_unparsed_emails:
        # Retry emails that went through the pipeline and were
        # initially unparsed
        filter = "unparsed"
    else:
        # Retrieve emails from the forwarding email specified in the .env
        filter = "forwarded"

    retrieved_emails = get_emails.main(filter)

    for email in retrieved_emails:
        email_count["retrieved"] = email_count.get("retrieved", 0) + 1
        # Store the retrieved email in the database's emails table
        email.id = emails.insert_email(email)

        # Parse the email into a txn
        txn = email_parser.main(email)
        logger.info(f"Email UID {email.uid} - attempting to parse...")
        if not txn:
            logger.info(f"Email UID {email.uid} - unparsed.")
            email_count["unparsed"] = email_count.get("unparsed", 0) + 1
            continue

        # Check if there's an identical txn in the DB already
        # If so, flag it
        flagged_txn = identical_txns.main(txn)

        # Write the txn to the database
        txns.insert_txn(flagged_txn)  # pragma: no cover
        logger.info(f"Email UID {email.uid} - successfully parsed!")

        # One down!
        email_count["processed"] = (
            email_count.get("processed", 0) + 1
        )  # pragma: no cover

    deduced_email_count = email_count.get("unparsed") + email_count.get("processed")
    retrieved_email_count = email_count.get("retrieved")
    if deduced_email_count != email_count.get("retrieved"):  # pragma: no cover
        logger.critical(
            f"FAILED: {retrieved_email_count} emails retrieved but {deduced_email_count} were accounted for."
        )
    logger.info(f"Total Emails in Batch = {retrieved_email_count}")
    logger.info(f"{email_count}")
    logger.info("DONE")
    return email_count


if __name__ == "__main__":  # pragma: no cover
    retry_unparsed_emails = False
    if len(sys.argv) == 2:
        retry_unparsed_emails = True
    email_count = main(retry_unparsed_emails)
