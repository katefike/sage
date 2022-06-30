import base64
import re
import datetime

def main(msg):
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
        html_data = None
    
    if not sender or subject or html_data:
        f"Sender: {sender}"
        f"Subject: {subject}"
        f"Body: {html_data}"

    # Parse the email based on who the sender is
    if sender == 'Chase <no.reply.alerts@chase.com>':
        bank = 'Chase'
        merchant, amount = parse_chase(subject)
    
    if html_data:
        if sender == 'Discover Card <discover@services.discover.com>':
            bank = 'Discover'
            if subject != 'Transaction Alert':
                return False
            merchant, amount = parse_discover(html_data)

        if sender == 'Huntington Alerts <HuntingtonAlerts@email.huntington.com>':
            bank = 'Huntington'
            if subject == 'Deposit':
                payer, amount = parse_huntington_deposit(html_data)
            elif subject == 'Withdrawal or Purchase':    
                merchant, amount = parse_huntington_charge(html_data)
            else:
                return False
            account = identify_huntington_account(html_data)
            balance = get_huntington_balance(html_data)

        gmail_id = msg['id']
        epoch_gmail_time = float(msg['internalDate'])
        gmail_time = datetime.datetime.fromtimestamp( epoch_gmail_time/ 1000.0).strftime('%Y-%m-%d %H:%M')
    
    transaction = {'Gmail ID': gmail_id, 'time': gmail_time, 'bank': bank, 
    'merchant': merchant, 'payer': payer, 'amount': amount, 'account': account, 'balance': balance}
    return transaction

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

def parse_discover(html_data: str) -> str:
    """
    Extract the transaction amount and merchant from the email body
    I.e.
    Transaction Date:: June 11, 2022

    Merchant: SQ *EARTH BISTRO CAFE

    Amount: $23.50
    """
    merchent = regex_search('(?<=Merchant: )(.*)(?=\n)', html_data)
    amount = regex_search('(?<=Amount: )(.*)(?=\n)', html_data)
    return merchent, amount

def parse_huntington_charge(html_data: str) -> str:
    """
    Extract the transaction amount and merchent from the email body
    I.e.
    We've processed an ACH withdrawal for $1.72 at CHASE CREDIT CRD EPAY 
    from your account nicknamed SAVE.
    """
    merchent = regex_search('(?<= at )(.*)(?= from your account nicknamed)', html_data)
    amount = regex_search('(?<=for \$)(.*)(?= at)', html_data)
    return merchent, amount

def parse_huntington_deposit(html_data: str) -> str:
    """
    Extract the transaction amount and merchent from the email body
    I.e.
    We've processed an ACH deposit for $59.81 
    from CHASE CREDIT CRD RWRD RDM to your account nicknamed CHECK.
    """
    payer = regex_search('(?<= from )(.*)(?= to your account nicknamed)', html_data)
    amount = regex_search('(?<=for \$)(.*)(?= from)', html_data)
    return payer, amount

def identify_huntington_account(html_data: str) -> str:
    """
    Identify the Huntington account referenced.
    Works for deposits or charges.
    I.e.
    We've processed an ACH withdrawal for $1.72 at CHASE CREDIT CRD EPAY 
    from your account nicknamed SAVE.
    """
    account = regex_search('(?<= your account nicknamed )(.*)(?=. That\'s above the)', html_data)
    if account == 'CHECK':
        account = 'Checking'
    if account == 'SAVE':
        account = 'Savings'
    return account

def get_huntington_balance(html_data: str) -> str:
    """
    Extract the account balance for Huntington savings or checking accounts.
    Works for deposits or charges.
    I.e.
    Your balance is $19,748.78 as of 6/25/22 2:35 AM ET.
    """
    balance = regex_search('(?<=Your balance is \$)(.*)(?=. as of)', html_data)
    return balance

def regex_search(pattern, string)-> str:
    results = re.search(pattern, string)
    if results:
        all_matches = results.group(0)
        return all_matches
    else:
        return None