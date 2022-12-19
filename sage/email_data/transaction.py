from dataclasses import dataclass, field
from datetime import datetime


@dataclass(init=True, repr=True)
class Transaction:
    """
    Represents a transaction in an email.
    """

    # pylint: disable=too-many-instance-attributes

    uid: int
    # Time the email was received by the mail server
    time_received: str
    # Transaction type can be one of the following
    # withdrawal: a merchant removed money from the account
    # deposit: a payer added money from the account
    # transfer withdrawal: I moved money out of this account to another account
    # or I withdrew cash from this account
    # transfer deposit: I moved money into this account from another account
    # or I deposited cash into this account
    type_: str = field(default=None)
    # Bank can be Huntington, Chase, Discover or cash
    bank: str = field(default=None)
    # Merchants perform withdrawals
    merchant: str = field(default=None)
    # Payers perform deposits
    payer: str = field(default=None)
    amount: str = field(default=None)
    # Not all banks have accounts. If there is no account listed that means there is
    # only one account associated with the bank.
    account: str = field(default=None)
    # Not all transactions list the account balance.
    balance: str = field(default=None)
