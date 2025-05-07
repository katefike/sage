from loguru import logger
from sage.parsers.utils import regex_search, RegexError


def get_txn_type(body: str) -> str:
    """
    Identify the Huntington txn type
    """
    type_ = None
    if regex_search("(We've processed a transfer withdrawal for )", body):
        type_ = "transfer withdrawal"
    elif regex_search("(We've processed a transfer deposit for )", body):
        type_ = "transfer deposit"
    elif regex_search("(We've processed an ACH withdrawal for )", body):
        type_ = "withdrawal"
    elif regex_search("(We've processed a debit card withdrawal for )", body):
        type_ = "withdrawal"
    elif regex_search("(We've processed an ACH deposit for )", body):
        type_ = "deposit"
    elif regex_search("(We've processed a deposit for )", body):
        type_ = "deposit"
    else:
        logger.warning("No Huntington txn type identified")
    return type_


def parse_transfer_withdrawal(body: str) -> str:
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


def parse_transfer_deposit(body: str) -> str:
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


def parse_withdrawal(body: str) -> tuple[str, str]:
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


def parse_deposit(body: str) -> tuple[str, str]:
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


def get_account(body: str) -> str:
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
        account = "asterisk-free checking"
    elif account == "CK2379":
        account = "perks checking"
    elif account == "SAVE":
        account = "savings"
    else:
        raise RegexError(
            f"Regex failed to get the account from a Huntington txn email body: {body}"
        )
    return account


def get_balance(body: str) -> str:
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
