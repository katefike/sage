import os.path
from types import BuiltinMethodType

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import base64
from bs4 import BeautifulSoup
import email
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
        results = service.users().messages().list(userId='me').execute()
        message_ids = results.get('messages', [])

        if not message_ids:
            print('No messages found.')
            return
        
        results = service.users().messages().list(userId='me').execute()
        messages = results.get('messages', [])
        messages = [service.users().messages().get(userId='me', id=msg['id']).execute() for msg in messages]

        for content in messages:
            headers = content['payload']['headers']
            for data in headers:
                if data['name'] == 'From':
                    sender = data['value']
                if data['name'] == 'Subject':
                    subject = data['value']
            
            if sender == 'Chase <no.reply.alerts@chase.com>':
                print(subject)

            message = None
            if "data" in content['payload']['body']:
                message = content['payload']['body']['data']
                message = data_encoder(message)
            elif "data" in content['payload']['parts'][0]['body']:
                message = content['payload']['parts'][0]['body']['data']
                message = data_encoder(message)
            else:
                print("body has no data.")
            if message:
                soup = BeautifulSoup(message, 'lxml')
                for elem in soup(text=re.compile(r' [$]\d\d[.]\d\d')):
                    print(elem.parent)


    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


def data_encoder(text):
    if len(text)>0:
        message = base64.urlsafe_b64decode(text)
        message = str(message, 'utf-8')
        # message = email.message_from_string(message)
    return message

if __name__ == '__main__':
    main()