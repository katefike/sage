import base64
from bs4 import BeautifulSoup
import re
import datetime

def main(messages):
    for msg in messages:

        headers = msg['payload']['headers']
        
        for data in headers:
            if data['name'] == 'From':
                sender = data['value']
            if data['name'] == 'Subject':
                subject = data['value']

        if "data" in msg['payload']['body']:
            str_data = msg['payload']['body']['data']
            html_data = data_encoder(str_data)
        elif "data" in msg['payload']['parts'][0]['body']:
            str_data = msg['payload']['parts'][0]['body']['data']
            html_data = data_encoder(str_data)
        else:
            print("The payload body has no data.")
    
        # Parse the email based on who the sender is
        if sender == 'Chase <no.reply.alerts@chase.com>':
            account = 'Chase'
            merchant, amount = parse_chase(subject)
            
        if sender == 'Discover Card <discover@services.discover.com>':
            account = 'Discover'
            parse_discover(subject, html_data)

        if sender == 'Huntington Alerts <HuntingtonAlerts@email.huntington.com>':
            account = 'Huntington'
            parse_huntington(html_data)

        gmail_id = msg['id']
        epoch_gmail_time = float(msg['internalDate'])
        gmail_time = datetime.datetime.fromtimestamp( epoch_gmail_time/ 1000.0).strftime('%Y-%m-%d %H:%M')
    return True

def data_encoder(str_data: str) -> str:
    if len(str_data)>0:
        byte_data = base64.urlsafe_b64decode(str_data)
        html_data = str(byte_data, 'utf-8')
    return html_data

def parse_chase(subject: str) -> str:
    """
    Extract the transaction amount and merchant from the email subject
    I.e.
    Your $1.00 transaction with DIGITALOCEAN.COM
    """
    merchant = regex_search("(?<=with )(.*)", subject)
    amount = regex_search("(?<=\$)(.*)(?= transaction)", subject)
    return merchant, amount

def parse_discover(subject, html_data):
    """
    Extract the transaction amount and merchant from the email body
    I.e.
    Transaction Date:: June 11, 2022

    Merchant: SQ *EARTH BISTRO CAFE

    Amount: $23.50
    """
    if subject != 'Transaction Alert':
        return False
    if html_data:
        merchent = regex_search('(?<=Merchant: )(.*)(?=\n)', html_data)
        amount = regex_search('(?<=Amount: )(.*)(?=\n)', html_data)
        return merchent, amount

def parse_huntington(html_data):
    if html_data:
        soup = BeautifulSoup(html_data, 'lxml')
        # for elem in soup(text=re.compile(r' (?<=\$)(.*)(?= transaction')):
        #     pass
            # print(subject)
            # print(elem.parent)

def regex_search(pattern, string):
    results = re.search(pattern, string)
    if results:
        all_matches = results.group(0)
        return all_matches
    else:
        return None