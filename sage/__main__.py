"""
This is starting point of the program. It steps through the following
tasks:

1. Load the environment variables.
2. Log into the email account on the mail server that is receiving the
forwarded alert emails. Retrieve emails that are from the forwarding email.
3. Store all retrieved emails in the database's emails table.
4. Process the transaction data contained in the email message:
    4a. Parse the transaction data from the email message.
    4b. Write the transaction data to the Postgres database.
"""
from datetime import datetime

import imap_tools
from loguru import logger

from sage.db import emails, transactions
from sage.models.email import Email
from sage.parsers import email_parser

from . import ENV

logger.add(sink="sage_main.log", level="INFO")


def main():
    logger.info("STARTING SAGE")

    # Set the time the batch started
    utc_timestamp = datetime.utcnow()
    batch_time = utc_timestamp.strftime("%Y-%m-%d %H:%M:%S")

    # Log into the receiving mailbox on the mail server and retrieve emails
    # that are from the forwarding email
    # Connect to the mailbox containing transaction alert emails
    with imap_tools.MailBoxUnencrypted(ENV["IMAP4_FQDN"]).login(
        ENV["RECEIVING_EMAIL_USER"], ENV["RECEIVING_EMAIL_PASSWORD"]
    ) as mailbox:

        msg_count = {
            "retrieved": 0,
            "unparsed": 0,
            "processed": 0,
        }

        # Retrieve all emails in the inbox from the forwarding email
        for msg in mailbox.fetch(imap_tools.A(from_=ENV["FORWARDING_EMAIL"])):

            msg_count["retrieved"] = msg_count.get("retrieved", 0) + 1

            # Store the retrieved email in the database's emails table
            # FIXME: Parse the origin email
            origin = "placeholder"
            # FIXME: body is set twice: once here and once in email_parser
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
            email_id = emails.insert_email(email)

            # Parse a email message into the transaction data
            transaction = email_parser.main(msg, email_id)
            if not transaction:
                logger.info(f"UID {msg.uid} was not parsed into a transaction.")
                msg_count["unparsed"] = msg_count.get("unparsed", 0) + 1
                continue

            # Write the transaction to the database
            transactions.insert_transaction(transaction)  # pragma: no cover

            # One down!
            msg_count["processed"] = (
                msg_count.get("processed", 0) + 1
            )  # pragma: no cover

    deduced_msg_count = msg_count.get("unparsed") + msg_count.get("processed")
    retrieved_msg_count = msg_count.get("retrieved")
    if deduced_msg_count != msg_count.get("retrieved"):  # pragma: no cover
        logger.critical("FAILED")
        logger.critical(
            f"ERROR-HANDLING ERROR: {retrieved_msg_count} msgs retrieved but {deduced_msg_count} were accounted for."
        )
    logger.info(f"Total Messages in Batch = {retrieved_msg_count}")
    logger.info(f"{msg_count}")
    logger.info("DONE")
    return msg_count


if __name__ == "__main__":  # pragma: no cover
    msg_count = main()
