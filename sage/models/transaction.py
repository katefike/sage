from dataclasses import dataclass, field


@dataclass(init=True, repr=True)
class Transaction:
    """
    Represents a transaction (txn) in an email.
    """

    # pylint: disable=too-many-instance-attributes

    # The ID of the email in the emails table
    # that this txn was parsed from
    email_id: int = field(default=None)
    # The ID of the txn in the txns table
    id: int = field(default=None)
    # Date the txn was made; based on the day the email was
    # originally sent by the institution;
    # not based on the day the email was forwarded.
    # ISO 8601 format; 1999-01-08. No time is included.
    date: str = field(default=None)
    # Txn type can be one of the following
    # withdrawal: a merchant removed money from the account
    # deposit: a payer added money from the account;
    # this includes credits and refunds
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
    # Not all banks have accounts. If there is no account listed that means
    # there is only one account associated with the bank.
    account: str = field(default=None)
    # Not all txns list the account balance.
    balance: str = field(default=None)
    # The ID of an older txn that's identical to this one
    identical_txn_id: id = field(default=None)
