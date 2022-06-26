import base64
from bs4 import BeautifulSoup
import re

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

        if sender == 'Huntington Alerts <HuntingtonAlerts@email.huntington.com>':
            account = 'Huntington'
            parse_huntington(html_data)

    
    return True

def data_encoder(str_data):
    if len(str_data)>0:
        byte_data = base64.urlsafe_b64decode(str_data)
        html_data = str(byte_data, 'utf-8')
    return html_data

def parse_chase(subject):
    """
    Extract the transaction amount and merchant from the email subject
    I.e.
    Your $1.00 transaction with DIGITALOCEAN.COM
    """
    amount = regex_search("(?<=\$)(.*)(?= transaction)", subject)
    merchant = regex_search("(?<=with )(.*)", subject)
    return merchant, amount

def parse_huntington(html_data):
    if html_data:
        soup = BeautifulSoup(html_data, 'lxml')
        # for elem in soup(text=re.compile(r' (?<=\$)(.*)(?= transaction')):
        #     pass
            # print(subject)
            # print(elem.parent)

def regex_search(pattern, string):
    results = re.search(pattern, string)
    all_matches = results.group(0)
    return all_matches