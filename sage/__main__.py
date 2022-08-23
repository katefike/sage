import os
import typing
from loguru import logger
import imaplib
import pathlib
from dotenv import load_dotenv

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
        logger.critical(".env not loaded")
    IMAP4_FQDN = os.environ.get("IMAP4_FQDN")
    IMAP4_PORT = os.environ.get("IMAP4_PORT")
    EMAIL_USER = os.environ.get("EMAIL_USER")
    EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
    mail = imaplib.IMAP4(IMAP4_FQDN, IMAP4_PORT)
    mail.login(EMAIL_USER, EMAIL_PASSWORD)
    mail.list()
    mail.select("inbox")  # connect to inbox.
    result, data = mail.search(None, "ALL")
    ids = data[0]  # data is a list.
    id_list = ids.split()  # ids is a space separated string
    latest_email_id = id_list[-1]  # get the latest
    # fetch the email body (RFC822) for the given ID
    result, data = mail.fetch(latest_email_id, "(RFC822)")

    raw_email = data[0][1]  # here's the body, which is raw text of the whole email
    # including headers and alternate payloads
    print(raw_email)
    # Get the message details
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
