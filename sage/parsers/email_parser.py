import re
from datetime import datetime

from loguru import logger

from sage.models.email import Email
from sage.models.transaction import Transaction

logger.add(sink="sage_main.log")


class RegexError(Exception):
    """Custom exception for indicating a regex match failure."""

    pass


def main(email: Email) -> Transaction:
    """
    Parse the txn data from the email.

    :param email: an Email object defined in sage.models.email.py
    :returns: a Transaction object defined in sage.models.transaction.py
    """
    txn = Transaction(email.id)
    # Identify who the bank is
    # TODO: Refactor this to only call get_bank once
    if not get_bank(email.body):
        return
    txn.bank = get_bank(email.body)
    # Parse the email based on who the bank is
    if txn.bank == "Chase":
        txn.type_ = get_chase_txn_type(email.subject)
        if txn.type_ == "deposit":
            txn.payer, raw_amount = parse_chase_deposit(email.body)
        elif txn.type_ == "withdrawal":
            txn.merchant, raw_amount = parse_chase_withdrawal(email.subject)
        else:
            return
    if txn.bank == "Discover":
        txn.type_ = "withdrawal"
        txn.merchant, raw_amount = parse_discover(email.body)
    if txn.bank == "Huntington":
        txn.type_ = get_huntington_txn_type(email.body)
        # Parse the Huntington txn based on the txn type
        if txn.type_ == "transfer withdrawal":
            raw_amount = parse_huntington_transfer_withdrawal(email.body)
        elif txn.type_ == "transfer deposit":
            raw_amount = parse_huntington_transfer_deposit(email.body)
        elif txn.type_ == "withdrawal":
            txn.merchant, raw_amount = parse_huntington_withdrawal(email.body)
        elif txn.type_ == "deposit":
            txn.payer, raw_amount = parse_huntington_deposit(email.body)
        else:
            return
        # Identify the Huntington account the txn occurred on
        txn.account = get_huntington_account(email.body)
        # Get the balance of the Huntington account
        raw_balance = get_huntington_balance(email.body)
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
        To: <example.com>
    E.g.
        ---------- Forwarded message ---------
        From: Chase <no.reply.alerts@chase.com>
        Date: Wed, 24 Apr 2024 18:33:10 -0400 (EDT)
        Subject: Your $253.36 transaction with AMZN Mktp US
        To: <example.com>
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
        To: <example.com>
    """
    if regex_search("(no.reply.alerts@chase.com)", body):
        return "Chase"
    elif regex_search("(discover@services.discover.com)", body):
        return "Discover"
    elif regex_search("(huntington.com)", body):
        return "Huntington"
    else:
        logger.warning("No bank identified")
    return


def get_chase_txn_type(subject: str) -> str:
    """
    Identify the Chase txn type
    """
    type_ = None
    if regex_search("( credit pending )", subject):
        type_ = "deposit"
    elif regex_search("( transaction with )", subject):
        type_ = "withdrawal"
    else:
        logger.warning("No Chase txn type identified")
    return type_


def parse_chase_deposit(body: str) -> str:
    """
    Extract the txn amount and payer from the email body
    E.g.
    Transaction alert
    You have a $1.63 credit pending on your credit card
    Account Prime Visa (...6104)
    Date Apr 3, 2024 at 11:48 AM ET
    Merchant RAPPI* VERIF $1.63 U
    Credit Amount $1.63
    """
    payer = regex_search(r"(?<=Merchant )(.*)(?= Credit Amount )", body)
    raw_amount = regex_search(
        r"(?<=Transaction alert You have a \$)(.*)(?= credit pending)", body
    )
    return payer, raw_amount


def parse_chase_withdrawal(subject: str) -> str:
    """
    Extract the txn amount and merchant from the email subject
    E.g.
    Your $1.00 transaction with DIGITALOCEAN.COM
    """
    merchant = regex_search(r"(?<=with )(.*)", subject)
    raw_amount = regex_search(r"(?<=\$)(.*)(?= transaction)", subject)
    return merchant, raw_amount


def parse_discover(body: str) -> str:
    """
    Extract the txn amount and merchant from the email body
    E.g.
    Transaction Date: June 11, 2022

    Merchant: SQ *EARTH BISTRO CAFE

    Amount: $23.50
    """
    merchant = regex_search(r"(?<=Merchant: )(.*)(?= Amount: )", body)
    raw_amount = regex_search(r"(?<=Amount: \$)([0-9]+(?:,[0-9]{3})?\.[0-9]{2})", body)
    return merchant, raw_amount


def get_huntington_txn_type(body: str) -> str:
    """
    Identify the Huntington txn type
    """
    type_ = None
    if regex_search("(We've processed a transfer withdrawal for )", body):
        type_ = "transfer withdrawal"
    elif regex_search("(We've processed a transfer deposit for )", body):
        type_ = "transfer deposit"
    elif regex_search("(We've processed an ACH withdrawal for)", body):
        type_ = "withdrawal"
    elif regex_search("(We've processed an ACH deposit for )", body):
        type_ = "deposit"
    elif regex_search("(We've processed a deposit for )", body):
        type_ = "deposit"
    else:
        logger.warning("No Huntington txn type identified")
    return type_


def parse_huntington_transfer_withdrawal(body: str) -> str:
    """
    Extract the transferred amount from the email body
    E.g.
    We've processed a transfer withdrawal for $999.51
    from your account nicknamed CHECK. That's above the $0.00 you set for an alert.
    """
    raw_amount = regex_search(
        r"(?:We've processed a transfer withdrawal for \$)(.*)(?= from your account nicknamed)",
        body,
    )
    if raw_amount is None:
        raise RegexError(
            f"Regex failed to get the raw amount from a Huntington transfer withdrawal email body: {body}"
        )
    return raw_amount


def parse_huntington_transfer_deposit(body: str) -> str:
    """
    Extract the tranferred amount from the email body
    E.g.
    We've processed a transfer deposit for $999.51 to your account nicknamed
    SAVE. That's above the $0.00 you set for an alert.
    """
    raw_amount = regex_search(
        r"(?<=We've processed a transfer deposit for \$)(.*)(?= to your account nicknamed)",
        body,
    )
    if raw_amount is None:

        raise RegexError(
            f"Regex failed to get the raw amount from a Huntington transfer deposit email body: {body}"
        )
    return raw_amount


def parse_huntington_withdrawal(body: str) -> str:
    """
    Extract the txn amount and merchant from the email body
    E.g.
    We've processed an ACH withdrawal for $1.72 at CHASE CREDIT CRD EPAY
    from your account nicknamed SAVE.
    E.g.
    We've processed an ACH withdrawal for $10,000.00 at TREASURY DIRECT TREAS DRCT from your account nicknamed SAVE.
    """
    raw_amount = regex_search(
        r"(?<=for \$)([0-9]+(?:,[0-9]{3})?\.[0-9]{2})(?= at)",
        body,
    )
    if raw_amount is None:
        raise RegexError(
            f"Regex failed to get the raw amount from a Huntington withdrawal email body: {body}"
        )
    merchant = regex_search(
        r"(?:for \$[0-9]+(?:,[0-9]{3})?\.[0-9]{2} at )(.*)(?= from your account nicknamed)",
        body,
    )
    if merchant is None:
        raise RegexError(
            f"Regex failed to get the merchant from a Huntington withdrawal email body: {body}"
        )
    return merchant, raw_amount


def parse_huntington_deposit(body: str) -> str:
    """
    Extract the txn amount and merchant from the email body
    E.g.
    We've processed an ACH deposit for $59.81
    from CHASE CREDIT CRD RWRD RDM to your account nicknamed CHECK.
    E.g.
    We've processed a deposit for $1,500.00 to your account nicknamed CHECK
    """
    raw_amount = regex_search(
        r"(?<= for \$)([0-9]+(?:,[0-9]{3})?\.[0-9]{2})(?= from)",
        body,
    )

    if raw_amount is None:
        # Cash deposit
        raw_amount = regex_search(
            r"(?<= for \$)([0-9]+(?:,[0-9]{3})?\.[0-9]{2})(?= to your account nicknamed)",
            body,
        )
        if raw_amount is None:
            raise RegexError(
                f"Regex failed to get the raw amount from a Huntington deposit email body: {body}"
            )
        payer = "cash"
        return payer, raw_amount

    payer = regex_search(
        r"(?: for \$[0-9]+(?:,[0-9]{3})?\.[0-9]{2} from )(.*)(?= to your account nicknamed)",
        body,
    )
    if payer is None:
        raise RegexError(
            f"Regex failed to get the payer from a Huntington deposit email body: {body}"
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
    elif account == "SAVE":
        account = "savings"
    else:
        raise RegexError(
            f"Regex failed to get the account from a Huntington txn email body: {body}"
        )
    return account


def get_huntington_balance(body: str) -> str:
    """
    Extract the account balance for Huntington savings or checking accounts.
    Works for deposits or charges.
    I.e.
    Your balance is $19,748.78 as of 6/25/22 2:35 AM ET.
    I.e.
    Your balance is -$101.92 as of 4/16/24 3:28 AM ET.
    """
    balance = regex_search(
        r"(?<=Your balance is \$)([0-9]+(,[0-9]{3})?\.[0-9]{2})(?= as of)", body
    )
    if balance is None:
        # Match a negative balance :(
        balance = regex_search(
            r"(?<=Your balance is -\$)([0-9]+(,[0-9]{3})?\.[0-9]{2})(?= as of)", body
        )
        if balance is None:
            raise RegexError(
                f"Regex failed to get the balance from a Huntington txn email body: {body}"
            )
        balance = "-" + balance
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
