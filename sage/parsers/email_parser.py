import re
from datetime import datetime

from loguru import logger

from sage.models.email import Email
from sage.models.transaction import Transaction
from sage.parsers.banks import chase, discover, huntington
from sage.parsers.utils import regex_search, transform_amount, RegexError

from . import BANKS_CONFIG

logger.add(sink="sage_main.log")

def main(email: Email) -> Transaction:
    """
    Parse the txn data from the email.

    :param email: an Email object defined in sage.models.email.py
    :returns: a Transaction object defined in sage.models.transaction.py
    """

    txn = Transaction(email.id)
    # Identify the bank from the email
    bank = get_bank(email.body)
    if not bank:
        return
    txn.bank = bank

    # Parse the email based on the bank
    if txn.bank == "Chase":
        txn.type_ = chase.get_txn_type(email.subject)
        if txn.type_ == "deposit":
            txn.payer, raw_amount = chase.parse_deposit(email.body)
        elif txn.type_ == "withdrawal":
            txn.merchant, raw_amount = chase.parse_withdrawal(email.subject)
        else:
            return
    elif txn.bank == "Discover":
        txn.type_ = "withdrawal"
        # Since 240628, only Discover student has sent txn emails
        # Discover miles and savings will be closed soon
        txn.account = "student"
        txn.merchant, raw_amount = discover.parse_withdrawal(email.body)
    elif txn.bank == "Huntington":
        txn.type_ = huntington.get_txn_type(email.body)
        # Parse the Huntington txn based on the txn type
        if txn.type_ == "transfer withdrawal":
            raw_amount = huntington.parse_transfer_withdrawal(email.body)
        elif txn.type_ == "transfer deposit":
            raw_amount = huntington.parse_transfer_deposit(email.body)
        elif txn.type_ == "withdrawal":
            txn.merchant, raw_amount = huntington.parse_withdrawal(email.body)
        elif txn.type_ == "deposit":
            txn.payer, raw_amount = huntington.parse_deposit(email.body)
        else:
            return
        # Identify the Huntington account the txn occurred on
        txn.account = huntington.get_account(email.body)
        # Get the balance of the Huntington account
        raw_balance = huntington.get_balance(email.body)
        txn.balance = transform_amount(raw_balance)
    # Don't return a txn object if the no amount could be determined.
    # The email was likely some other notification email from the bank.
    if not raw_amount:
        return
    txn.amount = transform_amount(raw_amount)
    # Identify the date the tansaction email arrived
    txn.date = get_date(email.body)
    return txn


def get_date(body: str) -> str:
    """
    Identify the date using the bank's email
    E.g.
        ---------- Forwarded message ---------
        From: Huntington Alerts <HuntingtonAlerts@email.huntington.com>
        Date: Thu, Oct 6, 2022 at 10:32 AM
        Subject: Withdrawal or Purchase
        To: <localhost>
    E.g.
        ---------- Forwarded message ---------
        From: Chase <no.reply.alerts@chase.com>
        Date: Wed, 24 Apr 2024 18:33:10 -0400 (EDT)
        Subject: Your $253.36 transaction with AMZN Mktp US
        To: <localhost>
    """
    # Match month, day, year format e.g. "Oct 6, 2022"
    raw_date = regex_search(
        r"(?<=Date: \w{3}, )(\w{3} [0-9]{1,2}, [0-9]{4})(?= at [0-9]{1,2}:[0-9]{2}\S|\s\w{2})",
        body,
    )
    if raw_date is not None:
        # Converts raw date to datetime object. E.g. "Oct 6, 2022"
        datetime_raw_date = datetime.strptime(raw_date, "%b %d, %Y")
        # Reformat the datetime object to ISO 8601 format
        transformed_date = datetime.strftime(datetime_raw_date, "%Y-%m-%d")
        return transformed_date

    # Match day month year format E.g. "24 Apr 2024"
    raw_date = regex_search(
        r"(?<=Date: \w{3}, )([0-9]{1,2} \w{3},? [0-9]{4})(?= [0-9]{2}:[0-9]{2}:[0-9]{2} )",
        body,
    )
    if raw_date is not None:
        # Converts raw date to datetime object. E.g. "24 Apr 2024"
        datetime_raw_date = datetime.strptime(raw_date, "%d %b %Y")
        # Reformat the datetime object to ISO 8601 format
        transformed_date = datetime.strftime(datetime_raw_date, "%Y-%m-%d")
        return transformed_date
    else:
        raise RegexError(f"Regex failed to get the date from body: {body}")


def get_bank(body: str) -> str:
    """
    Identify the bank using the bank's email
    E.g.
        ---------- Forwarded message ---------
        From: Huntington Alerts <HuntingtonAlerts@email.huntington.com>
        Date: Thu, Oct 6, 2022 at 10:32 AM
        Subject: Withdrawal or Purchase
        To: <localhost>
    """
    for bank, accounts in BANKS_CONFIG.items():
        for account in accounts:
            if regex_search(f"({account.get('email')})", body):
                return bank
    logger.warning("No bank identified")
    return None
