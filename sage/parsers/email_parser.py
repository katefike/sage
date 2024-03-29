import re
from datetime import datetime

from bs4 import BeautifulSoup
from imap_tools import MailMessage
from loguru import logger

from sage.models.transaction import Transaction

logger.add(sink="sage_main.log")


def main(msg: MailMessage, email_id: int) -> Transaction:
    """
    Parse the transaction data from the email.

    :param msg: this is an an email
    :param email_id: the ID in the database's emails table for this email
    :returns: this is a transaction object defined by the program
    """
    transaction = Transaction(email_id)
    # Get the email body
    if msg.text:
        body = msg.text
    elif msg.html:
        soup = BeautifulSoup(msg.html, "html.parser")
        body = soup.get_text(" ")

    # Identify who the bank is
    if not get_bank(body):
        return
    transaction.bank = get_bank(body)
    # Parse the email based on who the bank is
    if transaction.bank == "Chase":
        transaction.type_ = "withdrawal"
        transaction.merchant, raw_amount = parse_chase(msg.subject)
    if transaction.bank == "Discover":
        transaction.type_ = "withdrawal"
        transaction.merchant, raw_amount = parse_discover(body)
    if transaction.bank == "Huntington":
        transaction.type_ = get_huntington_transaction_type(body)
        # Parse the Huntington transaction based on the transaction type
        if transaction.type_ == "transfer withdrawal":
            raw_amount = parse_huntington_transfer_withdrawal(body)
        elif transaction.type_ == "transfer deposit":
            raw_amount = parse_huntington_transfer_deposit(body)
        elif transaction.type_ == "withdrawal":
            transaction.merchant, raw_amount = parse_huntington_withdrawal(body)
        elif transaction.type_ == "deposit":
            transaction.payer, raw_amount = parse_huntington_deposit(body)
        # Identify the Huntington account the transaction occurred on
        transaction.account = get_huntington_account(body)
        # Get the balance of the Huntington account
        raw_balance = get_huntington_balance(body)
        transaction.balance = transform_amount(raw_balance)
    # Don't return a transaction object if the no amount could be determined.
    # The email was likely some other notification email from the bank.
    if not raw_amount:
        return
    transaction.amount = transform_amount(raw_amount)
    # Identify the date the tansaction email arrived
    transaction.date = get_date(body)
    return transaction


def get_date(body: str) -> str:
    """
    Identify the date using the bank's email
    I.e.
        ---------- Forwarded message ---------
        From: Huntington Alerts <HuntingtonAlerts@email.huntington.com>
        Date: Thu, Oct 6, 2022 at 10:32 AM
        Subject: Withdrawal or Purchase
        To: <example.com>
    """
    raw_date = regex_search(
        r"(?<=Date: \w{3}, )(\w{3} [0-9]{1,2}, [0-9]{4})(?= at [0-9]{1,2}:[0-9]{2} \w{2} Subject: )",
        body,
    )
    # Converts raw date to datetime object. I.e. "Oct 6, 2022"
    datetime_raw_date = datetime.strptime(raw_date, "%b %d, %Y")
    # Reformat the datetime object to ISO 8601 format
    transformed_date = datetime.strftime(datetime_raw_date, "%Y-%m-%d")
    return transformed_date


def get_bank(body: str) -> str:
    """
    Identify the bank using the bank's email
    I.e.
        ---------- Forwarded message ---------
        From: Huntington Alerts <HuntingtonAlerts@email.huntington.com>
        Date: Thu, Oct 6, 2022 at 10:32 AM
        Subject: Withdrawal or Purchase
        To: <example.com>
    """
    if regex_search("(no.reply.alerts@chase.com)", body):
        return "Chase"
    elif regex_search("(discover@services.discover.com)", body):
        return "Discover"
    elif regex_search("(HuntingtonAlerts@email.huntington.com)", body):
        return "Huntington"
    return


def parse_chase(subject: MailMessage.subject) -> str:
    """
    Extract the transaction amount and merchant from the email subject
    I.e.
    Your $1.00 transaction with DIGITALOCEAN.COM
    """
    merchant = regex_search(r"(?<=with )(.*)", subject)
    raw_amount = regex_search(r"(?<=\$)(.*)(?= transaction)", subject)
    return merchant, raw_amount


def parse_discover(body: str) -> str:
    """
    Extract the transaction amount and merchant from the email body
    I.e.
    Transaction Date: June 11, 2022

    Merchant: SQ *EARTH BISTRO CAFE

    Amount: $23.50
    """
    merchant = regex_search(r"(?<=Merchant: )(.*)(?= Amount: )", body)
    raw_amount = regex_search(r"(?<=Amount: \$)([0-9]+(?:,[0-9]{3})?\.[0-9]{2})", body)
    return merchant, raw_amount


def get_huntington_transaction_type(body: str) -> str:
    """
    Identify the Huntington transaction type
    """
    if regex_search("(transfer withdrawal)", body):
        type_ = "transfer withdrawal"
    elif regex_search("(transfer deposit)", body):
        type_ = "transfer deposit"
    elif regex_search("(withdrawal)", body):
        type_ = "withdrawal"
    elif regex_search("(deposit)", body):
        type_ = "deposit"
    return type_


def parse_huntington_transfer_withdrawal(body: str) -> str:
    """
    Extract the transferred amount from the email body
    I.e.
    We've processed a transfer withdrawal for $999.51
    from your account nicknamed CHECK. That's above the $0.00 you set for an alert.
    """
    raw_amount = regex_search(
        r"(?:We've processed a transfer withdrawal for \$)(.*)(?= from your account nicknamed)",
        body,
    )
    return raw_amount


def parse_huntington_transfer_deposit(body: str) -> str:
    """
    Extract the tranferred amount from the email body
    I.e.
    We've processed a transfer deposit for $999.51 to your account nicknamed
    SAVE. That's above the $0.00 you set for an alert.
    """
    raw_amount = regex_search(
        r"(?<=We've processed a transfer deposit for \$)(.*)(?= to your account nicknamed)",
        body,
    )
    return raw_amount


def parse_huntington_withdrawal(body: str) -> str:
    """
    Extract the transaction amount and merchant from the email body
    I.e.
    We've processed an ACH withdrawal for $1.72 at CHASE CREDIT CRD EPAY
    from your account nicknamed SAVE.
    I.e.
    We've processed an ACH withdrawal for $10,000.00 at TREASURY DIRECT TREAS DRCT from your account nicknamed SAVE.
    """
    merchant = regex_search(
        r"(?:for \$[0-9]+(?:,[0-9]{3})?\.[0-9]{2} at )(.*)(?= from your account nicknamed)",
        body,
    )
    raw_amount = regex_search(
        r"(?<=for \$)([0-9]+(?:,[0-9]{3})?\.[0-9]{2})(?= at)",
        body,
    )
    return merchant, raw_amount


def parse_huntington_deposit(body: str) -> str:
    """
    Extract the transaction amount and merchant from the email body
    I.e.
    We've processed an ACH deposit for $59.81
    from CHASE CREDIT CRD RWRD RDM to your account nicknamed CHECK.
    """
    payer = regex_search(
        r"(?: for \$[0-9]+(?:,[0-9]{3})?\.[0-9]{2} from )(.*)(?= to your account nicknamed)",
        body,
    )
    raw_amount = regex_search(
        r"(?<= for \$)([0-9]+(?:,[0-9]{3})?\.[0-9]{2})(?= from)",
        body,
    )
    return payer, raw_amount


def get_huntington_account(body: str) -> str:
    """
    Identify the Huntington account referenced.
    Works for deposits or charges.
    I.e.
    We've processed an ACH withdrawal for $1.72 at CHASE CREDIT CRD EPAY
    from your account nicknamed SAVE.
    """
    account = regex_search(
        r"(?<= your account nicknamed )(\w*)(?=. That's above the)", body
    )
    if account == "CHECK":
        account = "checking"
    if account == "SAVE":
        account = "savings"
    return account


def get_huntington_balance(body: str) -> str:
    """
    Extract the account balance for Huntington savings or checking accounts.
    Works for deposits or charges.
    I.e.
    Your balance is $19,748.78 as of 6/25/22 2:35 AM ET.
    """
    balance = regex_search(
        r"(?<=Your balance is \$)([0-9]+(,[0-9]{3})?\.[0-9]{2})(?= as of)", body
    )
    return balance


def transform_amount(raw_amount: str) -> int:
    # Remove the comma
    raw_amount = re.sub(",", "", raw_amount)
    # Check for decimals
    if regex_search(r"(.\d{2})", raw_amount):
        transformed_amount = raw_amount
    else:
        transformed_amount = raw_amount + ".00"
    return transformed_amount


def regex_search(pattern: str, raw_text: str) -> str:
    transformed_text = raw_text.replace("\r", "").replace("\n", " ")
    match = re.search(pattern, transformed_text, flags=re.DOTALL | re.MULTILINE)
    if match:
        group_1 = match.group(1)
        return group_1
