"""
Insert a transaction into the transactions table.
"""

from typing import List

from loguru import logger

from sage.db import banks, entities, execute_statements
from sage.models.transaction import Transaction

logger.add(sink="sage_main.log")


def insert_transaction(transaction: Transaction) -> bool:
    bank_id = banks.get_id(transaction.bank, transaction.account)
    # Transfers don't have entities
    if "transfer" in transaction.type_:
        transaction_data = (
            transaction.email_id,
            transaction.date,
            bank_id,
            transaction.type_,
            transaction.amount,
        )
        stmt = """
        INSERT INTO
            transactions (email_id, date, bank_id, type, amount)
        VALUES
            (%s, %s, %s, %s, %s);
        """
    else:
        entity_id = entities.get_id(transaction.merchant, transaction.payer)
        transaction_data = (
            transaction.email_id,
            transaction.date,
            bank_id,
            transaction.type_,
            transaction.amount,
            entity_id,
        )
        stmt = """
        INSERT INTO
            transactions (email_id, date, bank_id, type, amount, entity_id)
        VALUES
            (%s, %s, %s, %s, %s, %s);
        """
    row_count = execute_statements.insert(stmt, transaction_data)
    return row_count


def get_transactions_by_daterange(start_date: str, stop_date: str) -> List[tuple]:
    select_criteria = (start_date, stop_date)
    stmt = """
    SELECT
        *
    FROM
        transactions
    WHERE
        date >= %s
        AND date <= %s;
    """
    records = execute_statements.select(stmt, select_criteria)
    return records
