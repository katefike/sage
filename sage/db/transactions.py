"""
Insert a transaction into the transactions table.
"""

from loguru import logger

from sage.db import banks, entities, execute_statements
from sage.email_data.transaction import Transaction

logger.add(sink="sage_main.log")


def insert_transaction(transaction: Transaction) -> bool:
    bank_id = banks.get_id(transaction.bank, transaction.account)
    # Transfers don't have entities
    if "transfer" in transaction.type_:
        transaction_data = (
            transaction.date,
            bank_id,
            transaction.type_,
            transaction.amount,
        )
        stmt = """
        INSERT INTO
            transactions (date, bank_id, type, amount)
        VALUES
            (%s, %s, %s, %s);
        """
    else:
        entity_id = entities.get_id(transaction.merchant, transaction.payer)
        transaction_data = (
            transaction.date,
            bank_id,
            transaction.type_,
            transaction.amount,
            entity_id,
        )
        stmt = """
        INSERT INTO
            transactions (date, bank_id, type, amount, entity_id)
        VALUES
            (%s, %s, %s, %s, %s);
        """
    row_count = execute_statements.insert(stmt, transaction_data)
    return row_count
