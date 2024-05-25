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


def get_complete_transactions_by_daterange(
    start_date: str, stop_date: str
) -> List[tuple]:
    select_criteria = (start_date, stop_date)
    stmt = """
    SELECT t.id,
        t.date,
        b.name AS "bank_name",
        e.name AS "entity_name",
        CASE
            WHEN t.type = 'withdrawal' THEN t.amount * -1
            ELSE t.amount
        END
    FROM transactions t
        JOIN banks b ON b.id = t.bank_id
        JOIN entities e ON e.id = t.entity_id
    WHERE t.date >= %s t.AND date <= %s
    ORDER BY t.date ASC;
    """
    records = execute_statements.select(stmt, select_criteria)
    return records
