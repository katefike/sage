import imap_tools
from db import transactions
from email_parser import email_parser
from loguru import logger

from . import ENV

logger.add(sink="debug.log", level="INFO")

# TODO: Add more vertical linespace to separate concepts


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

    # Log into the receiving mailbox on the mail server and retrieve emails
    # that have a UID that is greater than the maximum UID in the database.
    max_uid = transactions.get_maximum_uid()

    # Connect to the mailbox containing transaction alert emails
    with imap_tools.MailBoxUnencrypted(ENV["IMAP4_FQDN"]).login(
        ENV["RECEIVING_EMAIL_USER"], ENV["RECEIVING_EMAIL_PASSWORD"]
    ) as mailbox:
        msg_count = {
            "retrieved": 0,
            "rejected": 0,
            "unparsed": 0,
            "processed": 0,
        }

        # Retrieve emails that are greater than the maximum UID
        # and are from the forwarding email
        for msg in mailbox.fetch(
            imap_tools.A(
                uid=imap_tools.U(f"{max_uid + 1}", "*"),
                from_=ENV["FORWARDING_EMAIL"],
            )
        ):
            msg_count["retrieved"] = msg_count.get("retrieved", 0) + 1

            # TODO: Move to parsing module
            # Ignore emails that don't have a text or html body
            # This seems unlikely but who knows
            # Change from or to and
            if not msg.text and not msg.html:
                logger.warning(
                    f"Rejecting email from {msg.from_} because it doesn't have a message body."
                )
                msg_count["rejected"] = msg_count.get("rejected", 0) + 1
                continue

            # Parse a email message into the transaction data
            transaction = email_parser.main(msg)

            if not transaction:
                logger.info(f"UID {msg.uid} was not parsed into a transaction.")
                msg_count["unparsed"] = msg_count.get("unparsed", 0) + 1
                continue

            # TODO: Generate array of transactions and batch insert into DB
            # Write the transaction to the database
            transactions.insert_transaction(transaction)  # pragma: no cover

            # One down!
            msg_count["processed"] = (
                msg_count.get("processed", 0) + 1
            )  # pragma: no cover

    deduced_msg_count = (
        msg_count.get("rejected")
        + msg_count.get("unparsed")
        + msg_count.get("processed")
    )
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
