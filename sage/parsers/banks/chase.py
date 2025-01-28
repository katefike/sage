from loguru import logger
from sage.parsers.utils import regex_search, transform_amount

def get_txn_type(subject: str) -> str:
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

def parse_deposit(body: str) -> tuple[str, str]:
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

def parse_withdrawal(subject: str) -> tuple[str, str]:
    """
    Extract the txn amount and merchant from the email subject
    E.g.
    Your $1.00 transaction with DIGITALOCEAN.COM
    """
    merchant = regex_search(r"(?<=with )(.*)", subject)
    raw_amount = regex_search(r"(?<=\$)(.*)(?= transaction)", subject)
    return merchant, raw_amount
