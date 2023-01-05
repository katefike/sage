"""
Insert a transaction into the transactions table.
"""

from db import banks, entities, execute_statements
from email_data.transaction import Transaction
from loguru import logger

logger.add(sink="debug.log")


def get_maximum_uid() -> int:
    stmt = """
        SELECT MAX(uid) FROM transactions;
        """
    results = execute_statements.select(stmt)
    max_uid = results[0][0]
    # Upon starting the program for the first time, get UIDs greater than zero
    # Zero is not a valid UID; they start with 1.
    if not max_uid:
        max_uid = 0
    return max_uid


def insert_transaction(transaction: Transaction) -> bool:
    bank_id = banks.get_id(transaction.bank, transaction.account)
    # Transfers don't have entities
    if "transfer" in transaction.type_:
        transaction_data = (
            transaction.uid,
            transaction.date,
            bank_id,
            transaction.type_,
            transaction.amount,
        )
        stmt = """
        INSERT INTO
            transactions (uid, date, bank_id, type, amount)
        VALUES
            (%s, %s, %s, %s, %s);
        """
    else:
        entity_id = entities.get_id(transaction.merchant, transaction.payer)
        transaction_data = (
            transaction.uid,
            transaction.date,
            bank_id,
            transaction.type_,
            transaction.amount,
            entity_id,
        )
        stmt = """
        INSERT INTO
            transactions (uid, date, bank_id, type, amount, entity_id)
        VALUES
            (%s, %s, %s, %s, %s, %s);
        """
    row_count = execute_statements.insert(stmt, transaction_data)
    return row_count
