import os.path
from types import BuiltinMethodType

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import base64
from bs4 import BeautifulSoup
import re

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def main():
    """
    DOCSTRING EVENTUALLY
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        # List the messages in the mailbox.
        results = service.users().messages().list(userId='me').execute()
        if not results:
            print('No messages found.')
            return

        message_ids = results['messages']
        # Get the message details
        messages = [service.users().messages().get(userId='me', id=msg_id['id']).execute() for msg_id in message_ids]

        for msg in messages:
            headers = msg['payload']['headers']
            
            for data in headers:
                if data['name'] == 'From':
                    sender = data['value']
                if data['name'] == 'Subject':
                    subject = data['value']
            
            if sender == 'Chase <no.reply.alerts@chase.com>':
                pass
                # print(subject)

            str_data = None
            if "data" in msg['payload']['body']:
                str_data = msg['payload']['body']['data']
                html_data = data_encoder(str_data)
            elif "data" in msg['payload']['parts'][0]['body']:
                str_data = msg['payload']['parts'][0]['body']['data']
                html_data = data_encoder(str_data)
            else:
                print("The payload body has no data.")

            if html_data:
                soup = BeautifulSoup(html_data, 'lxml')
                for elem in soup(text=re.compile(r' [$]\d\d[.]\d\d')):
                    print(subject)
                    # print(elem.parent)



    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


def data_encoder(str_data):
    if len(str_data)>0:
        byte_data = base64.urlsafe_b64decode(str_data)
        html_data = str(byte_data, 'utf-8')
    return html_data

if __name__ == '__main__':
    main()