import os
import typing
from loguru import logger
import pathlib
from dotenv import load_dotenv
import imap_tools

# from email_parser import email_parser
# from db import db_transactions

logger.add(sink="debug.log")


def main():
    """
    DOCSTRING EVENTUALLY
    """
    app_root = str(pathlib.Path(__file__).parent.parent)
    env_path = app_root + "/.env"
    if not load_dotenv(env_path):
        logger.critical(".env failed to load.")
    IMAP4_FQDN = os.environ.get("IMAP4_FQDN")
    FORWARDING_EMAIL = os.environ.get("FORWARDING_EMAIL")
    RECEIVING_EMAIL = os.environ.get("RECEIVING_EMAIL")
    RECEIVING_EMAIL_PASSWORD = os.environ.get("RECEIVING_EMAIL_PASSWORD")

    with imap_tools.MailBoxUnencrypted(IMAP4_FQDN).login(
        RECEIVING_EMAIL, RECEIVING_EMAIL_PASSWORD
    ) as mailbox:
        for msg in mailbox.fetch():
            print(msg.uid, msg.to, msg.from_, msg.subject, msg.text)

    # TODO: Hand over the emails to the rest of the app
    # for msg_id in message_ids:
    #     message = (
    #         service.users().messages().get(userId="me", id=msg_id["id"]).execute()
    #     )
    #     parsed_email = email_parser.main(message)

    #     if parsed_email and parsed_email.get("transaction"):
    #         db_transactions.insert_transaction(parsed_email)
    #         logger.info("Success")
    #         # db_transactions.write_transaction(transaction)
    # logger.info("DONE")
    return


if __name__ == "__main__":
    main()
