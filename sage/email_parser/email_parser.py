import re

from imap_tools import MailMessage
from loguru import logger

from sage.email_data.transaction import Transaction

logger.add(sink="debug.log")


def main(msg: MailMessage) -> Transaction:
    """
    Parse the transaction data from the email.
    """
    transaction = Transaction(int(msg.uid))

    if msg.text:
        body = msg.text
    elif msg.html:
        body = msg.html
    # Identify who the bank is
    transaction.bank = identify_bank(body)
    # Parse the email based on who the bank is
    if transaction.bank == "Chase":
        transaction.type_ = "withdrawal"
        transaction.merchant, raw_amount = parse_chase(msg.subject)
    if transaction.bank == "Discover":
        transaction.type_ = "withdrawal"
        transaction.merchant, raw_amount = parse_discover(body)
    if transaction.bank == "Huntington":
        transaction.type_ = identify_huntington_transaction_type(body)
        # Parse the Huntington transaction based on the transaction type
        if transaction.type_ == "transfer withdrawal":
            raw_amount = parse_huntington_transfer_withdrawal(body)
        elif transaction.type_ == "transfer deposit":
            raw_amount = parse_huntington_transfer_deposit(body)
        elif transaction.type_ == "withdrawal":
            transaction.merchant, raw_amount = parse_huntington_withdrawal(body)
        elif transaction.type_ == "deposit":
            transaction.payer, raw_amount = parse_huntington_deposit(body)
        transaction.account = identify_huntington_account(body)
    transaction.amount = transform_amount(raw_amount)
    return transaction


def identify_bank(body: str) -> str:
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
        bank = "Chase"
    elif regex_search("(discover@services.discover.com)", body):
        bank = "Discover"
    elif regex_search("(HuntingtonAlerts@email.huntington.com)", body):
        bank = "Huntington"
    return bank


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
    raw_amount = regex_search(r"(?<=Amount: )(\$[0-9]+(?:,[0-9]{3})?\.[0-9]{2})", body)
    return merchant, raw_amount


def identify_huntington_transaction_type(body: str) -> str:
    """
    Identify the Huntington transaction type
    """
    if regex_search("transfer withdrawal", body):
        type_ = "transfer withdrawal"
    elif regex_search("transfer deposit", body):
        type_ = "transfer deposit"
    elif regex_search("withdrawal", body):
        type_ = "withdrawal"
    elif regex_search("deposit", body):
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
        get_full_match=False,
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
        get_full_match=False,
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
        get_full_match=False,
    )
    raw_amount = regex_search(r"(?<=for \$)(.*)(?= at)", body)
    return merchant, raw_amount


def parse_huntington_deposit(body: str) -> str:
    """
    Extract the transaction amount and merchant from the email body
    I.e.
    We've processed an ACH deposit for $59.81
    from CHASE CREDIT CRD RWRD RDM to your account nicknamed CHECK.
    """
    payer = regex_search(
        r"(?:for \$[0-9]+(?:,[0-9]{3})?\.[0-9]{2} from )(.*)(?= to your account nicknamed)",
        body,
        get_full_match=False,
    )
    raw_amount = regex_search(r"(?<=for \$)(.*)(?=from)", body)
    return payer, raw_amount


def identify_huntington_account(body: str) -> str:
    """
    Identify the Huntington account referenced.
    Works for deposits or charges.
    I.e.
    We've processed an ACH withdrawal for $1.72 at CHASE CREDIT CRD EPAY
    from your account nicknamed SAVE.
    """
    account = regex_search(
        r"(?<= your account nicknamed )(.*)(?=. That's above the)", body
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
    balance = regex_search(r"(?<=Your balance is \$)(.*)(?=. as of)", body)
    return balance


def transform_amount(raw_amount: str) -> int:
    # Remove the comma
    raw_amount = re.sub(",", "", raw_amount)
    # Check for decimals
    if regex_search(r"(.\d\d)", raw_amount):
        transformed_amount = raw_amount
    else:
        transformed_amount = raw_amount + ".00"
    return transformed_amount


def regex_search(pattern: str, raw_input: str, get_full_match=True) -> str:
    transformed_input = raw_input.replace("\r", "").replace("\n", " ")
    print("-----REGEX STRING---")
    print(transformed_input)
    print("-----PATTERN---")
    print(pattern)
    match = re.search(pattern, transformed_input, flags=re.DOTALL | re.MULTILINE)
    if match:
        if not get_full_match:
            group = match.group(1)
            return group
        full_match = match.group(0)
        return full_match
