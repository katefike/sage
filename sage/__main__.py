import os
import typing
from loguru import logger
import imaplib
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
    IMAP4_PORT = os.environ.get("IMAP4_PORT")
    FORWARDING_EMAIL = os.environ.get("FORWARDING_EMAIL")
    RECEIVING_EMAIL = os.environ.get("RECEIVING_EMAIL")
    RECEIVING_EMAIL_PASSWORD = os.environ.get("RECEIVING_EMAIL_PASSWORD")
    # conn = imaplib.IMAP4(IMAP4_FQDN, IMAP4_PORT)
    # conn.login(RECEIVING_EMAIL, RECEIVING_EMAIL_PASSWORD)
    # Get date, subject and body len of all emails from INBOX folder
    with imap_tools.MailBoxUnencrypted(IMAP4_FQDN).login(
        RECEIVING_EMAIL, RECEIVING_EMAIL_PASSWORD
    ) as mailbox:
        for msg in mailbox.fetch():
            print(msg.date, msg.subject, len(msg.text or msg.html))

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
