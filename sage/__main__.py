import os.path
import typing
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email_parser import email_parser
from db import db_transactions

LOGGER = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
    """
    DOCSTRING EVENTUALLY
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        # List the messages in the mailbox.
        results = service.users().messages().list(userId="me", maxResults=500).execute()
        if not results:
            print("No messages found.")
            return

        # TODO: Perform a partial synchronization once the history of message IDs is stored
        message_ids = results["messages"]
        # Get the message details
        for msg_id in message_ids:
            message = (
                service.users().messages().get(userId="me", id=msg_id["id"]).execute()
            )
            transaction = email_parser.main(message)

            if transaction:
                db_transactions.write_transaction(transaction)

        LOGGER.info("DONE")
        exit

    except HttpError as error:
        # TODO: Handle errors from gmail API
        LOGGER.error(f"An error occurred: {error}")


if __name__ == "__main__":
    main()