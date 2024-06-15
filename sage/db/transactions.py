"""
CRUD functions for the txns table.
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
        txn_data = (
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
        if not transaction.merchant and not transaction.payer:
            logger.critical(f"No merchant or payer for txn: {transaction}")
        entity_id = entities.get_id(transaction.merchant, transaction.payer)
        txn_data = (
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
    row_count = execute_statements.insert(stmt, txn_data)
    return row_count


def get_complete_transactions_by_daterange(
    start_date: str, stop_date: str
) -> List[tuple]:
    criteria = (start_date, stop_date)
    stmt = """
    SELECT
        t.id AS "transaction_id",
        t.email_id AS "email_id",
        t.date,
        b.name AS "bank_name",
        b.account AS "bank_account",
        e.name AS "entity_name",
        CASE
            WHEN t.type = 'withdrawal' THEN t.amount * -1
            ELSE t.amount
        END
    FROM transactions t
        JOIN banks b ON b.id = t.bank_id
        JOIN entities e ON e.id = t.entity_id
    WHERE t.date >= %s AND t.date <= %s
    ORDER BY t.date ASC;
    """
    row = execute_statements.select(stmt, criteria)
    return row


def get_identical_txn_id(txn: Transaction) -> tuple:
    """
    Identify the oldest txn that has the same attributes as the current txn.
    """
    bank_id = banks.get_id(txn.bank, txn.account)
    if "transfer" in txn.type_:
        criteria = (
            txn.date,
            txn.type_,
            bank_id,
            txn.amount,
        )
        stmt = """
        SELECT
            MIN(t.id) AS "txn_id"
        FROM transactions t
        WHERE t.date = %s
            AND t.type = %s
            AND t.bank_id = %s
            AND t.amount = %s;
        """
    else:
        entity_id = entities.get_id(txn.merchant, txn.payer)
        criteria = (
            txn.date,
            txn.type_,
            bank_id,
            txn.amount,
            entity_id,
        )
        stmt = """
        SELECT
            MIN(t.id) AS "txn_id"
        FROM transactions t
        WHERE t.date = %s
            AND t.type = %s
            AND t.bank_id = %s
            AND t.amount = %s
            AND t.entity_id = %s;
        """
    result, _column = execute_statements.select(stmt, criteria)
    identical_txn_id = result[0][0]
    return identical_txn_id
